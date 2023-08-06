from __future__ import annotations

import ctypes
from dataclasses import is_dataclass
from types import GenericAlias
from typing import Annotated

import pytest

from decoratools.capi import POINTER, bind, structure, union


def test_pointer_type_annotation():
    assert isinstance(POINTER[ctypes.c_int], GenericAlias)


def test_pointer_wrapper():
    assert POINTER(ctypes.c_int) == ctypes.POINTER(ctypes.c_int)


def test_structure_retains_name_docstring_and_annotations():
    class Point:
        """
        A 2D point
        """
        x: ctypes.c_int
        y: ctypes.c_int

    StructPoint = structure(Point)

    for attribute in ("__name__", "__doc__", "__annotations__"):
        assert getattr(StructPoint, attribute) == getattr(Point, attribute)


def test_structure_ctypes():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    assert issubclass(Point, ctypes.Structure)
    assert Point._fields_ == [("x", ctypes.c_int), ("y", ctypes.c_int)]


def test_structure_dataclass():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    assert is_dataclass(Point)


def test_structure_anonymous_fields():
    @structure
    class XCoordinate:
        x: ctypes.c_int

    @structure
    class YCoordinate:
        y: ctypes.c_int

    @structure
    class Point:
        foo: Annotated[XCoordinate, "decoratools.capi.anonymous"]
        bar: Annotated[YCoordinate, "decoratools.capi.anonymous"]

    assert Point._anonymous_ == (
        "foo",
        "bar",
    )


def test_structure_some_bindings_must_be_delayed():
    with pytest.raises(NameError, match="Link"):

        @structure
        class Link:
            previous: POINTER[Link]
            next: POINTER[Link]


def test_structure_delayed_binding():
    @structure(autobind=False)
    class Link:
        previous: POINTER[Link]
        next: POINTER[Link]

    bind(Link)
    assert Link._fields_ == [("previous", POINTER(Link)), ("next", POINTER(Link))]


def test_structure_delayed_binding_with_custom_global_type_resolution():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    @structure
    class _Point:
        x: ctypes.c_int
        y: ctypes.c_int
        _id: ctypes.c_int

    def segment():
        @structure(autobind=False)
        class Segment:
            start: Point
            end: Point

        bind(Segment, globals={"Point": _Point})

        return Segment

    assert segment()._fields_ == [("start", _Point), ("end", _Point)]


def test_structure_delayed_binding_with_custom_local_type_resolution():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    @structure
    class _Point:
        x: ctypes.c_int
        y: ctypes.c_int
        _id: ctypes.c_int

    @structure(autobind=False)
    class Segment:
        start: Point
        end: Point

    bind(Segment, locals={"Point": _Point})

    assert Segment._fields_ == [("start", _Point), ("end", _Point)]


def test_structure_packed():
    @structure
    class Unpacked:
        x: ctypes.c_int
        y: ctypes.c_int

    with pytest.raises(AttributeError, match="_pack_"):
        Unpacked._pack_

    @structure(pack=64)
    class Packed:
        x: ctypes.c_int
        y: ctypes.c_int

    assert Packed._pack_ == 64


@pytest.mark.parametrize(
    ("endianness", "expected"),
    [
        pytest.param("native", ctypes.Structure, id="native"),
        pytest.param("little", ctypes.LittleEndianStructure, id="little-endian"),
        pytest.param("big", ctypes.BigEndianStructure, id="big-endian"),
    ]
)
def test_structure_endianness(
    endianness: str,
    expected: type[ctypes.Structure | ctypes.LittleEndianStructure | ctypes.BigEndianStructure],
):
    @structure(endianness=endianness)
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    assert issubclass(Point, expected)


def test_structure_invalid_endianness():
    with pytest.raises(ValueError, match="invalid"):
        structure(endianness="invalid")


@pytest.mark.parametrize(
    ("illegal_dataclass_kwarg",),
    [
        pytest.param("init", id="init, to not override Structure's"),
        pytest.param("frozen", id="frozen, to be compatible with Structure's descriptors"),
        pytest.param("slots", id="slots, to be compatible with Structure's descriptors"),
        pytest.param("wearkref_slots", id="weakref_slots, out of consistency wrt slots"),
    ],
)
def test_structure_illegal_dataclass_kwargs(illegal_dataclass_kwarg: str):
    with pytest.raises(TypeError, match=illegal_dataclass_kwarg):
        structure(**{illegal_dataclass_kwarg: None})


def test_union_ctypes():
    @structure(autobind=False)
    class BinaryBranch:
        left: POINTER[BinaryNode]
        right: POINTER[BinaryNode]

    @structure
    class Leaf:
        value: ctypes.c_void_p

    @union
    class BinaryNode:
        branch: POINTER[BinaryBranch]
        leaf: POINTER[Leaf]

    bind(BinaryBranch)

    assert issubclass(BinaryNode, ctypes.Union)
    assert BinaryNode._fields_ == [("branch", POINTER(BinaryBranch)), ("leaf", POINTER(Leaf))]


def test_union_dataclass():
    @structure(autobind=False)
    class BinaryBranch:
        left: POINTER[BinaryNode]
        right: POINTER[BinaryNode]

    @structure
    class Leaf:
        value: ctypes.c_void_p

    @union
    class BinaryNode:
        branch: POINTER[BinaryBranch]
        leaf: POINTER[Leaf]

    bind(BinaryBranch)

    assert is_dataclass(BinaryNode)


def test_union_anonymous_fields():
    @structure
    class XCoordinate:
        x: ctypes.c_int

    @structure
    class YCoordinate:
        y: ctypes.c_int

    @union
    class Coordinate:
        x: Annotated[XCoordinate, "decoratools.capi.anonymous"]
        y: Annotated[YCoordinate, "decoratools.capi.anonymous"]

    assert Coordinate._anonymous_ == (
        "x",
        "y",
    )


def test_union_some_bindings_must_be_delayed():
    with pytest.raises(NameError, match="TBD"):
        @union
        class _:
            backward: TBD  # noqa: F821
            forward: TBD   # noqa: F821


def test_union_delayed_bindings():
    @union(autobind=False)
    class Direction:
        backward: TBD  # noqa: F821
        forward: TBD   # noqa: F821

    bind(Direction, locals={"TBD": POINTER[Direction]})


def test_union_delayed_binding_with_custom_global_type_resolution():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    @structure
    class _Point:
        x: ctypes.c_int
        y: ctypes.c_int
        _id: ctypes.c_int

    def cursor():
        @union(autobind=False)
        class Cursor():
            point: Point
            location: Point

        bind(Cursor, globals={"Point": _Point})

        return Cursor

    assert cursor()._fields_ == [("point", _Point), ("location", _Point)]


def test_union_delayed_binding_with_custom_local_type_resolution():
    @structure
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    @structure
    class _Point:
        x: ctypes.c_int
        y: ctypes.c_int
        _id: ctypes.c_int

    @union(autobind=False)
    class Cursor():
        point: Point
        location: Point

    bind(Cursor, locals={"Point": _Point})

    assert Cursor._fields_ == [("point", _Point), ("location", _Point)]


def test_union_packed():
    @union
    class Unpacked:
        x: ctypes.c_int
        y: ctypes.c_int

    with pytest.raises(AttributeError, match="_pack_"):
        Unpacked._pack_

    @union(pack=64)
    class Packed:
        x: ctypes.c_int
        y: ctypes.c_int

    assert Packed._pack_ == 64


@pytest.mark.parametrize(
    ("endianness", "expected"),
    [
        pytest.param("native", ctypes.Union, id="native"),
        pytest.param("little", ctypes.LittleEndianUnion, id="little-endian"),
        pytest.param("big", ctypes.BigEndianUnion, id="big-endian"),
    ]
)
def test_union_endianness(
    endianness: str,
    expected: type[ctypes.Union | ctypes.LittleEndianUnion | ctypes.BigEndianUnion],
):
    @union(endianness=endianness)
    class Point:
        x: ctypes.c_int
        y: ctypes.c_int

    assert issubclass(Point, expected)


def test_union_invalid_endianness():
    with pytest.raises(ValueError, match="invalid"):
        union(endianness="invalid")


@pytest.mark.parametrize(
    ("illegal_dataclass_kwarg",),
    [
        pytest.param("init", id="init, to not override Union's"),
        pytest.param("frozen", id="frozen, to be compatible with Union's descriptors"),
        pytest.param("slots", id="slots, to be compatible with Union's descriptors"),
        pytest.param("wearkref_slots", id="weakref_slots, out of consistency wrt slots"),
    ],
)
def test_union_illegal_dataclass_kwargs(illegal_dataclass_kwarg: str):
    with pytest.raises(TypeError, match=illegal_dataclass_kwarg):
        union(**{illegal_dataclass_kwarg: None})
