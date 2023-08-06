import ctypes
from collections.abc import Callable, Iterator
from functools import wraps
from inspect import currentframe, get_annotations
from types import GenericAlias
from typing import Any, get_args, get_origin, get_type_hints


class ARRAY:
    def __class_getitem__(cls, *args):
        return GenericAlias(cls, *args)


@wraps(ctypes.POINTER, updated=())
class POINTER(Callable):
    def __new__(cls, *args, **kwargs):
        return ctypes.POINTER(*args, **kwargs)

    def __class_getitem__(cls, *args):
        return GenericAlias(cls, *args)


def _fields(cls: type, globals: dict[str, Any], locals: dict[str, Any]) -> Iterator[tuple[str, type]]:
    for key, value in get_type_hints(cls, globalns=globals, localns=locals).items():
        if get_origin(value) is POINTER:
            yield key, ctypes.POINTER(*get_args(value))
        elif get_origin(value) is ARRAY:
            ctype, length = get_args(value)
            yield key, ctype * length
        else:
            yield key, value


def bind(
    cls: type[ctypes.Structure] | type[ctypes.Union],
    *,
    globals: dict[str, Any] | None = None,
    locals: dict[str, Any] | None = None,
) -> None:
    context = currentframe().f_back
    if globals is None:
        globals = context.f_globals
    if locals is None:
        locals = context.f_locals

    cls._anonymous_ = tuple(_anonymous(cls, globals=globals, locals=locals))
    cls._fields_ = list(_fields(cls, globals=globals, locals=locals))


def _anonymous(cls: type, globals: dict[str, Any], locals: dict[str, Any]) -> Iterator[str]:
    for key, value in get_annotations(cls, globals=globals, locals=locals, eval_str=True).items():
        if "decoratools.capi.anonymous" in get_args(value):
            yield key


def structure(
    cls: type | None = None,
    *,
    autobind: bool = True,
    pack: int | None = None,
    endianness: str = "native",
) -> type | Callable[[type], type]:
    context = currentframe().f_back
    match endianness:
        case "native":
            structure = ctypes.Structure
        case "little":
            structure = ctypes.LittleEndianStructure
        case "big":
            structure = ctypes.BigEndianStructure
        case _:
            raise ValueError(
                f"expected 'endianness' to be one of: 'native', 'little', or 'big', but got '{endianness}'"
            )

    def wrapper(cls: type) -> type:
        @wraps(cls, updated=())
        class Wrap(cls, structure):
            if autobind:
                _anonymous_ = tuple(_anonymous(cls, globals=context.f_globals, locals=context.f_locals))
                _fields_ = list(_fields(cls, globals=context.f_globals, locals=context.f_locals))
            if pack is not None:
                _pack_ = pack

        return Wrap

    if cls is None:
        return wrapper

    return wrapper(cls)


def union(
    cls: type | None = None,
    *,
    autobind: bool = True,
    pack: int | None = None,
    endianness: str = "native",
) -> type | Callable[[type], type]:
    context = currentframe().f_back
    match endianness:
        case "native":
            union = ctypes.Union
        case "little":
            union = ctypes.LittleEndianUnion
        case "big":
            union = ctypes.BigEndianUnion
        case _:
            raise ValueError(
                f"expected 'endianness' to be one of: 'native', 'little', or 'big', but got '{endianness}'"
            )

    def wrapper(cls: type) -> type:
        @wraps(cls, updated=())
        class Wrap(cls, union):
            if autobind:
                _anonymous_ = tuple(_anonymous(cls, globals=context.f_globals, locals=context.f_locals))
                _fields_ = list(_fields(cls, globals=context.f_globals, locals=context.f_locals))
            if pack is not None:
                _pack_ = pack

        return Wrap

    if cls is None:
        return wrapper

    return wrapper(cls)
