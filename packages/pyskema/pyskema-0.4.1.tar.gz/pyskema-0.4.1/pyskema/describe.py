"""Implement a function to describe a schema in human readable text."""

from .schema import Node, Atom, AtomType, Record, Tuple
from .visitor import Visitor
from .misc import closest, lev_dist, Result


def describe(schema, selects=()):
    """Describe in human readable format :code:`schema`.

    :param schema: The schema to describe.
    :param selects: (optional, :code:`()`) a path into
        schema to describe a sub-tree element only.
    """
    res = select(schema, selects)

    if not res:
        i = res.error

        if i == 0:
            raise KeyError(f"There is no {selects[0]} field in this schema.")
        else:
            raise KeyError(
                f"There is no {selects[i]} field in " + ".".join(selects[:i]) + "."
            )

    if selects != ():
        print(".".join(selects) + ":")

    for s in Describer.describe(res.value):
        print(s)


def select(schema, selects, index=0):
    if selects in {("all",), ("",), ()}:
        return Result.ok(schema)

    if index < len(selects) - 1:
        if (
            isinstance(schema.structure, (Record, Tuple))
            and selects[index] in schema.structure.fields
        ):
            node = schema.structure.fields[selects[index]]
            return select(node, selects, index=index + 1)
        else:
            return Result.error(index)
    else:
        return Result.ok(schema.structure.fields[selects[index]])


class Describer(Visitor):
    """A visitor that implement description.

    You should probably be using :func:`describe` instead.
    """
    @classmethod
    def describe(cls, schema):
        "Generate a set lines describing schema."
        yield from cls().describe_node(schema)

    def visit_atom(self, atom, indent=0):
        indent_str = "  " * indent
        message = [f"{indent_str}"]

        if atom.type_ == AtomType.OPTION:
            if len(atom.options) == 1:
                message.append(repr(atom.options[0]))
            else:
                message.append("one of ")
                message.append(", ".join(map(repr, atom.options[:-1])))
                message.append(f", or {repr(atom.options[-1])}")
        else:
            message.append(f"value of type {atom.type_.name()}")

        yield "".join(message)

    def visit_union(self, union, indent=0):
        indent_str = "  " * indent

        if len(union.options) > 1:
            yield indent_str + "one of the following options:"
            pfx = indent_str + "- "
            ind = indent + 1
        else:
            pfx = ""
            ind = indent

        for op in union.options:
            yield from self.describe_node(op, prefix=pfx, indent=ind)

    def visit_record(self, rec, indent=0):
        indent_str = "  " * indent
        for key, node in rec.fields.items():
            yield from self.describe_node(
                node, prefix=f"{indent_str}{key}: ", indent=indent + 1,
            )

    def visit_tuple(self, tup, indent=0):
        indent_str = "  " * indent
        for value in tup.fields:
            yield from self.describe_node(
                value, prefix=f"{indent_str}- ", indent=indent + 1,
            )

    def visit_collection(self, collection, indent=0):
        indent_str = "  " * indent
        yield f"{indent_str}a list of{indent_str}"
        yield from self.visit(collection.element, indent=indent + 1)

    def visit_map(self, map, indent=0):
        yield from self.visit(
            map.element, indent=indent + 1
        )

    def describe_node(self, value, prefix="", indent=0):
        indent_str = "  " * indent
        message = [prefix]

        if value.optional:
            message.append(
                f"(optional, default is {repr(value.default)})"
            )

        if value.description:
            if value.optional:
                message.append("\n" + indent_str)

            indented_descr = []

            first, *rest = value.description.split("\n")

            indented_descr.append(first)

            for line in rest:
                indented_descr.append(indent_str + line)

            message.append("\n".join(indented_descr))

        msg = "".join(message)

        if msg:
            yield msg

        yield from self.visit(value, indent=indent + 1)


def search(schema, name):
    "Search for name into schema."
    likely = sorted(Searcher.search(schema, name))
    return [".".join(p) for _, p in likely]


class Searcher(Visitor):
    "A visitor implementing the search."

    @classmethod
    def search(cls, schema, name):
        """Show the visit"""
        yield from cls().visit(schema, name)

    def visit_atom(self, atom, name, path=()):
        return ()

    def visit_union(self, union, name, path=()):
        for op in union.options:
            yield from self.visit(op, name, path)

    def visit_record(self, rec, name, path=()):
        for key, node in rec.fields.items():
            yield (lev_dist(key, name), (*path, key))
            yield from self.visit(node, name, (*path, key))

    def visit_tuple(self, tup, name, path=()):
        for i, value in enumerate(tup.fields):
            yield from self.visit(
                value,
                name,
                (*path, i),
            )

    def visit_collection(self, collection, name, path=()):
        yield from self.visit(collection.element, name, path)

    def visit_map(self, map, name, path=()):
        yield from self.visit(map.element, name, path)
