import json
import threading
import typing
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch

from muutils.json_serialize.array import load_array
from muutils.json_serialize.json_serialize import ObjectPath
from muutils.json_serialize.util import (
    ErrorMode,
    JSONdict,
    JSONitem,
    safe_getsource,
    string_as_lines,
)
from muutils.tensor_utils import DTYPE_MAP, TORCH_DTYPE_MAP
from muutils.zanj.externals import (
    GET_EXTERNAL_LOAD_FUNC,
    ZANJ_MAIN,
    ZANJ_META,
    ExternalItem,
    _ZANJ_pre,
)

# pylint: disable=protected-access, dangerous-default-value


@dataclass
class LoaderHandler:
    """handler for loading an object from a json file or a ZANJ archive"""

    # TODO: add a separate "asserts" function?
    # right now, any asserts must happen in `check` or `load` which is annoying with lambdas

    # (json_data, path) -> whether to use this handler
    check: Callable[[JSONitem, ObjectPath, _ZANJ_pre], bool]
    # function to load the object (json_data, path) -> loaded_obj
    load: Callable[[JSONitem, ObjectPath, _ZANJ_pre], Any]
    # unique identifier for the handler, saved in __format__ field
    uid: str
    # source package of the handler -- note that this might be overridden by ZANJ
    source_pckg: str
    # priority of the handler, defaults are all 0
    priority: int = 0
    # description of the handler
    desc: str = "(no description)"

    def serialize(self) -> JSONdict:
        """serialize the handler info"""
        return {
            # get the code and doc of the check function
            "check": {
                "code": safe_getsource(self.check),
                "doc": string_as_lines(self.check.__doc__),
            },
            # get the code and doc of the load function
            "load": {
                "code": safe_getsource(self.load),
                "doc": string_as_lines(self.load.__doc__),
            },
            # get the uid, source_pckg, priority, and desc
            "uid": str(self.uid),
            "source_pckg": str(self.source_pckg),
            "priority": int(self.priority),
            "desc": str(self.desc),
        }

    @classmethod
    def from_formattedclass(cls, fc: type, priority: int = 0):
        """create a loader from a class with `serialize`, `load` methods and `__format__` attribute"""
        assert hasattr(fc, "serialize")
        assert callable(fc.serialize)  # type: ignore
        assert hasattr(fc, "load")
        assert callable(fc.load)  # type: ignore
        assert hasattr(fc, "__format__")
        assert isinstance(fc.__format__, str)  # type: ignore

        return cls(
            check=lambda json_item, path=None, z=None: json_item["__format__"]
            == fc.__format__,
            load=lambda json_item, path=None, z=None: fc.load(json_item, path, z),
            uid=fc.__format__,
            source_pckg=str(fc.__module__),
            priority=priority,
            desc=f"formatted class loader for {fc.__name__}",
        )


# NOTE: there are type ignores on the loaders, since the type checking should be the responsibility of the check function

LOADER_MAP_LOCK = threading.Lock()

LOADER_MAP: dict[str, LoaderHandler] = {
    lh.uid: lh
    for lh in [
        # array external
        LoaderHandler(
            check=lambda json_item, path=None, z=None: (  # type: ignore[misc]
                isinstance(json_item, typing.Mapping)
                and "__format__" in json_item
                and json_item["__format__"].startswith("numpy.ndarray")
                # and json_item["data"].dtype.name == json_item["dtype"]
                # and tuple(json_item["data"].shape) == tuple(json_item["shape"])
            ),
            load=lambda json_item, path=None, z=None: np.array(load_array(json_item), dtype=DTYPE_MAP[json_item["dtype"]]),  # type: ignore[misc]
            uid="numpy.ndarray",
            source_pckg="muutils.zanj",
            desc="numpy.ndarray loader",
        ),
        LoaderHandler(
            check=lambda json_item, path=None, z=None: (  # type: ignore[misc]
                isinstance(json_item, typing.Mapping)
                and "__format__" in json_item
                and json_item["__format__"].startswith("torch.Tensor")
                # and json_item["data"].dtype.name == json_item["dtype"]
                # and tuple(json_item["data"].shape) == tuple(json_item["shape"])
            ),
            load=lambda json_item, path=None, z=None: torch.tensor(load_array(json_item), dtype=TORCH_DTYPE_MAP[json_item["dtype"]]),  # type: ignore[misc]
            uid="torch.Tensor",
            source_pckg="muutils.zanj",
            desc="torch.Tensor loader",
        ),
        # pandas
        LoaderHandler(
            check=lambda json_item, path=None, z=None: (  # type: ignore[misc]
                isinstance(json_item, typing.Mapping)
                and "__format__" in json_item
                and json_item["__format__"].startswith("pandas.DataFrame")
                and "data" in json_item
                and isinstance(json_item["data"], typing.Sequence)
            ),
            load=lambda json_item, path=None, z=None: pd.DataFrame(json_item["data"]),  # type: ignore[misc]
            uid="pandas.DataFrame",
            source_pckg="muutils.zanj",
            desc="pandas.DataFrame loader",
        ),
        # list/tuple external
        LoaderHandler(
            check=lambda json_item, path=None, z=None: (  # type: ignore[misc]
                isinstance(json_item, typing.Mapping)
                and "__format__" in json_item
                and json_item["__format__"].startswith("list")
                and "data" in json_item
                and isinstance(json_item["data"], typing.Sequence)
            ),
            load=lambda json_item, path=None, z=None: [
                load_item_recursive(x, path, z) for x in json_item["data"]
            ],
            uid="list",
            source_pckg="muutils.zanj",
            desc="list loader, for externals",
        ),
        LoaderHandler(
            check=lambda json_item, path=None, z=None: (  # type: ignore[misc]
                isinstance(json_item, typing.Mapping)
                and "__format__" in json_item
                and json_item["__format__"].startswith("tuple")
                and "data" in json_item
                and isinstance(json_item["data"], typing.Sequence)
            ),
            load=lambda json_item, path=None, z=None: tuple(
                [load_item_recursive(x, path, z) for x in json_item["data"]]
            ),
            uid="tuple",
            source_pckg="muutils.zanj",
            desc="tuple loader, for externals",
        ),
    ]
}


def register_loader_handler(handler: LoaderHandler):
    """register a custom loader handler"""
    global LOADER_MAP, LOADER_MAP_LOCK
    with LOADER_MAP_LOCK:
        LOADER_MAP[handler.uid] = handler


def get_item_loader(
    json_item: JSONitem,
    path: ObjectPath,
    zanj: _ZANJ_pre | None = None,
    error_mode: ErrorMode = "warn",
    # lh_map: dict[str, LoaderHandler] = LOADER_MAP,
) -> LoaderHandler | None:
    """get the loader for a json item"""
    global LOADER_MAP

    # check if we recognize the format
    if isinstance(json_item, typing.Mapping) and "__format__" in json_item:
        if not isinstance(json_item["__format__"], str):
            raise TypeError(
                f"invalid __format__ type '{type(json_item['__format__'])}' in '{path=}': '{json_item['__format__'] = }'"
            )
        if json_item["__format__"] in LOADER_MAP:
            return LOADER_MAP[json_item["__format__"]]

    # if we dont recognize the format, try to find a loader that can handle it
    for key, lh in LOADER_MAP.items():
        if lh.check(json_item, path, zanj):
            return lh

    # if we still dont have a loader, return None
    return None


def load_item_recursive(
    json_item: JSONitem,
    path: ObjectPath,
    zanj: _ZANJ_pre | None = None,
    error_mode: ErrorMode = "warn",
    allow_not_loading: bool = True,
) -> Any:
    lh: LoaderHandler | None = get_item_loader(
        json_item=json_item,
        path=path,
        zanj=zanj,
        error_mode=error_mode,
        # lh_map=lh_map,
    )

    if lh is not None:
        # special case for serializable dataclasses
        if (
            isinstance(json_item, typing.Mapping)
            and ("__format__" in json_item)
            and ("SerializableDataclass" in json_item["__format__"])
        ):
            # why this horribleness?
            # SerializableDataclass, if it has a field `x` which is also a SerializableDataclass, will automatically call `x.__class__.load()`
            # However, we need to load things in containers, as well as arrays
            processed_json_item: dict = {
                key: (
                    val
                    if (
                        isinstance(val, typing.Mapping)
                        and ("__format__" in val)
                        and ("SerializableDataclass" in val["__format__"])
                    )
                    else load_item_recursive(
                        json_item=val,
                        path=tuple(path) + (key,),
                        zanj=zanj,
                        error_mode=error_mode,
                    )
                )
                for key, val in json_item.items()
            }

            return lh.load(processed_json_item, path, zanj)

        else:
            return lh.load(json_item, path, zanj)
    else:
        if isinstance(json_item, dict):
            return {
                key: load_item_recursive(
                    json_item=json_item[key],
                    path=tuple(path) + (key,),
                    zanj=zanj,
                    error_mode=error_mode,
                    # lh_map=lh_map,
                )
                for key in json_item
            }
        elif isinstance(json_item, list):
            return [
                load_item_recursive(
                    json_item=x,
                    path=tuple(path) + (i,),
                    zanj=zanj,
                    error_mode=error_mode,
                    # lh_map=lh_map,
                )
                for i, x in enumerate(json_item)
            ]
        elif isinstance(json_item, (str, int, float, bool, type(None))):
            return json_item
        else:
            if allow_not_loading:
                return json_item
            else:
                raise ValueError(
                    f"unknown type {type(json_item)} at {path}\n{json_item}"
                )


class LoadedZANJ:
    """for loading a zanj file"""

    def __init__(
        self,
        path: str | Path,
        zanj: _ZANJ_pre,
    ) -> None:
        # path and zanj object
        self._path: str = str(path)
        self._zanj: _ZANJ_pre = zanj

        # load zip file
        self._zipf: zipfile.ZipFile = zipfile.ZipFile(file=self._path, mode="r")

        # load data
        self._meta: JSONdict = json.load(self._zipf.open(ZANJ_META, "r"))
        self._json_data: JSONitem = json.load(self._zipf.open(ZANJ_MAIN, "r"))

        # read externals
        self._externals: dict[str, ExternalItem] = dict()
        for fname, ext_item in self._meta["externals_info"].items():  # type: ignore[union-attr]
            item_type: str = ext_item["item_type"]
            with self._zipf.open(fname, "r") as fp:
                self._externals[fname] = ExternalItem(
                    item_type=item_type,  # type: ignore[arg-type]
                    data=GET_EXTERNAL_LOAD_FUNC(item_type)(self, fp),
                    path=ext_item["path"],
                )

    def populate_externals(self) -> None:
        """put all external items into the main json data"""

        for ext_path, ext_item in self._externals.items():
            # get the path to the item
            path: ObjectPath = tuple(ext_item.path)
            assert len(path) > 0
            assert all(
                isinstance(key, (str, int)) for key in path
            ), f"improper types in path {path=}"
            # get the item
            item = self._json_data
            for key in path:
                if not key in item:
                    raise KeyError(
                        f"could not find {key=} in {item=} for {ext_path=}, {ext_item=}"
                    )
                item = item[key]  # type: ignore[index]
            # replace the item with the external item
            assert "$ref" in item  # type: ignore
            assert item["$ref"] == ext_path  # type: ignore
            item["data"] = ext_item.data  # type: ignore

            item = load_item_recursive(
                json_item=item,
                path=path,
                zanj=self._zanj,
            )
