"The core definition of a schema."

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from abc import abstractmethod


class Structure:
    """Abstract structure of a node"""

    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        pass

    @classmethod
    def structure_default(cls):
        raise ValueError(
            f"In {cls} it is an error to set the node optional without a default value."
        )


@dataclass
class Node:
    """Base class for a node of the schema"""

    structure: Structure
    description: Optional[str] = None
    optional: bool = False
    default: Any = None

    def __init__(
        self,
        structure: Structure,
        description: Optional[str] = None,
        optional: bool = False,
        default: Any = None,
    ):
        r"""Create a :class:`Node` instance.

        :param structure: a :class:`Structure` instance describing the node.
        :param describing: (optional, :code:`None`) a human readable description
            as a :code:`str`.
        :param optional: (optional, :code:`False`) wether the node can be
            omited or not when part of a record.
        :param default: (optiona, :code:`None`) a default value used when the
            node is :code:`optional` and omited.
        """
        self.structure = structure
        self.description = description
        self.optional = optional
        self.default = default

        if self.optional and self.default is None:
            self.default = self.structure.structure_default()

    @classmethod
    def of_atom(cls, atom, options=None, **kwargs):
        r"""Constructor for an :class:`Atom` node.

        :param atom: the :class:`AtomType` for the node.
        :param options: options for :class:`Atom` constructor.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Atom(atom, options=options), **kwargs)

    @classmethod
    def of_union(cls, options, **kwargs):
        r"""Constructor for a :class:`Union` node.

        :param options: list of :class:`Node` instances for the alternatives.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Union(options), **kwargs)

    @classmethod
    def of_collection(cls, element, **kwargs):
        r"""Constructor for a :class:`Collection` node.

        :param element: the :class:`Node` instance describing an element of the
            collection.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Collection(element), **kwargs)

    @classmethod
    def of_record(cls, fields, **kwargs):
        r"""Constructor for a :class:`Record` node.

        :param fields: a :code:`dict` of :code:`str`
        :param options: options for :class:`Atom` constructor.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Record(fields), **kwargs)

    @classmethod
    def of_map(cls, element, **kwargs):
        r"""Constructor for a :class:`Map` node.

        :param element: the :class:`Node` instance describing an element of
            the map.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Map(element), **kwargs)

    @classmethod
    def of_tuple(cls, elements, **kwargs):
        r"""Constructor for a :class:`Tuple` node.

        :param elements: list of :class:`Node` describing the elements of the
            tuple.
        :param \*\*kwargs: kw parameters for :class:`Node.__init__`.
        """
        return cls(Tuple(elements), **kwargs)

    def inject(self, path, elem):
        """Inject new nodes or replace nodes in an exisisting schema.

        The original object is not altered, but a new schema is created instead
        with the same nodes (except for the injection).

        :param path: a tuple of :code:`str` and :code:`int` to indicate the
            place to modify. Use the names of record fields and the index of
            tuple fields and unions alternatives.
        :param elem: the element to insert at :code:`path`
        :returns: a fresh schema of the same structure as :code:`self` with due
            modifications.

        Example:

            >>> s1 = Node.of_record({
                "foo": Node.of_tuple([
                    Node.of_atom(AtomType.INT, description="width"),
                    Node.of_atom(AtomType.INT, description="height"),
                ]),
                "bar": Node.of_atom(AtomType.STR),
            })
            >>> s2 = s1.inject(("foo", 2), Node.of_atom(AtomType.INT, description="depth"))
            >>> describe(s1)
            foo: 
                - width
                    value of type int
                - height
                    value of type int
            bar: 
                value of type str
            >>> describe(s2)
            foo: 
                - width
                    value of type int
                - height
                    value of type int
                - depth
                    value of type int
            bar: 
                value of type str
        """
        from .edit import Injecter

        if not path:
            raise ValueError("You cannot delete with an empty path.")

        return Injecter().visit(self, path, elem)

    def delete(self, path):
        """Remove a node from an exisisting schema.

        The original object is not altered, but a new schema is created instead
        with the same nodes (except for the deletion).

        :param path: a tuple of :code:`str` and :code:`int` to indicate the
            place to modify. Use the names of record fields and the index of
            tuple fields and unions alternatives.
        :returns: a fresh schema of the same structure as :code:`self` with due
            modifications.

        Example:

            >>> s1 = Node.of_record({
                "foo": Node.of_tuple([
                    Node.of_atom(AtomType.INT, description="width"),
                    Node.of_atom(AtomType.INT, description="height"),
                    Node.of_atom(AtomType.INT, description="depth"),
                ]),
                "bar": Node.of_atom(AtomType.STR),
            })
            >>> s2 = s1.delete(("foo", 2))
            >>> describe(s1)
            foo: 
                - width
                    value of type int
                - height
                    value of type int
                - depth
                    value of type int
            bar: 
                value of type str
            >>> describe(s2)
            foo: 
                - width
                    value of type int
                - height
                    value of type int
            bar: 
                value of type str
        """
        from .edit import Deleter

        if not path:
            raise ValueError("You cannot delete with an empty path.")

        return Deleter().visit(self, path)

    def copy(self):
        "Deep copy of the schema."
        from .visitor import CopyingVisitor
        return CopyingVisitor().visit(self)


class AtomType(Enum):
    "Kind of atomic value."

    INT = 0
    FLOAT = 1
    STR = 2
    BOOL = 3
    OPTION = 4

    def name(self, options=None):
        "Return the type name."
        if self == self.INT:
            return "int"
        elif self == self.FLOAT:
            return "float"
        elif self == self.BOOL:
            return "bool"
        elif self == self.STR:
            return "str"
        elif self == self.OPTION:
            return "option(" + ", ".join(repr(s) for s in options) + ")"
        else:
            raise NotImplementedError("This type is not yet named...")


@dataclass
class Atom(Structure):
    """Structure of an atomic piece of data"""

    type_: AtomType
    options: Optional[List[str]] = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_atom(self, *args, **kwargs)


@dataclass
class Union(Structure):
    """Structure for the union of several nodes"""

    options: List[Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_union(self, *args, **kwargs)


@dataclass
class Collection(Structure):
    """An ordered collection of similar nodes"""

    element: Node

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_collection(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return []


@dataclass
class Record(Structure):
    """A key-value pair collection.

    Keys are from a defined set and values are defined per-key.
    Keys are supposed to be valid identifiers.
    """

    fields: Dict[str, Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_record(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return {}


@dataclass
class Map(Structure):
    """A key-value pair collection.

    Keys are not restricted and values are of a single type.
    """

    element: Node

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_map(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return {}


@dataclass
class Tuple(Structure):
    """A fixed set of ordered fields.

    Each field can have a different structure.
    """

    fields: List[Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_tuple(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return []
