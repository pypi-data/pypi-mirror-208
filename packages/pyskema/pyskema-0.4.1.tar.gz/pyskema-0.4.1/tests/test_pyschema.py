import pytest

from pyskema import AtomType, Node, validate
from pyskema.validate import InvalidDataError


def test_atom():
    u = Node.of_atom(AtomType.INT)
    assert validate(45, u) == 45


def test_union():
    u = Node.of_union([Node.of_atom(AtomType.INT), Node.of_atom(AtomType.FLOAT)])

    assert validate(45, u) == (Node.of_atom(AtomType.INT), 45)
    assert validate(3.14, u) == (Node.of_atom(AtomType.FLOAT), 3.14)


def test_collection_valid():
    u = Node.of_collection(Node.of_atom(AtomType.INT))
    assert validate([1, 2], u) == [1, 2]


def test_collection_invalid_item():
    u = Node.of_collection(Node.of_atom(AtomType.INT))
    with pytest.raises(InvalidDataError):
        validate([1, 2, 4.6], u)


def test_collection_str():
    u = Node.of_collection(Node.of_atom(AtomType.STR))
    with pytest.raises(InvalidDataError):
        validate("abc", u)


def test_record():
    u = Node.of_record(
        {
            "a": Node.of_atom(AtomType.INT),
            "b": Node.of_atom(AtomType.FLOAT, optional=True, default=45.0),
        }
    )

    assert validate({"a": 78}, u) == {"a": 78, "b": 45.0}

    with pytest.raises(InvalidDataError):
        validate({"b": 78}, u)


def test_collection_of_union():
    schema = Node.of_collection(
        Node.of_union(
            [
                Node.of_atom(AtomType.INT),
                Node.of_atom(AtomType.FLOAT),
            ]
        )
    )

    assert validate([1, 2, 4.6], schema) == [
        (Node.of_atom(AtomType.INT), 1),
        (Node.of_atom(AtomType.INT), 2),
        (Node.of_atom(AtomType.FLOAT), 4.6),
    ]
    with pytest.raises(InvalidDataError):
        validate([1, 2, "foo", 4.6], schema)
