"""Create a new schema with edits.

Internally used to implement :func:`schema.Node.inject` and :func:`schema.Node.delete`.
"""
from .visitor import CopyingVisitor
from .schema import Union, Record, Tuple


class Injecter(CopyingVisitor):
    "Visitor implementing :func:`schema.Node.inject`."

    def visit_atom(self, atom, path, _element):
        if path:
            raise ValueError("Invalid path leading to an atom in inject.")

        return super().visit_atom(atom)

    def visit_union(self, union, path, element):
        assert path, "empty path is not valid"

        j, *rest = path

        new_opts = []

        for i, node in union.options:
            if i != j:
                new_opts.append(node.copy())
            elif not rest:
                new_opts.append(element)
            else:
                new_opts.append(self.visit(node, rest, element))

        return Union(new_opts)

    def visit_record(self, rec, path, element):
        assert path, "empty path is not valid"

        fname, *rest = path

        fields = {}

        for name, node in rec.fields.items():
            if fname != name:
                fields[name] = node.copy()
            elif not rest:
                fields[fname] = element
            else:
                fields[fname] = self.visit(node, rest, element)

        if fname not in rec.fields:
            if rest:
                raise ValueError(f"Invalid path leading to non-existing branch {fname}")
            else:
                fields[fname] = element

        return Record(fields)

    def visit_tuple(self, tup, path, element):
        assert path, "empty path is not valid"

        j, *rest = path

        fields = []

        for i, node in enumerate(tup.fields):
            if i != j:
                fields.append(node.copy())
            elif not rest:
                fields.append(element)
            else:
                fields.append(self.visit(node, rest, element))

        if j == len(tup.fields) or j == -1:
            if rest:
                raise ValueError("Invalid path leading to non-existing branch.")
            else:
                fields.append(element)

        return Tuple(fields)


class Deleter(CopyingVisitor):
    "Visitor implementing :func:`schema.Node.delete`."

    def visit_atom(self, atom, path):
        assert path, "empty path is not valid"

        return super().visit_atom(atom)

    def visit_union(self, union, path):
        assert path, "empty path is not valid"

        j, *rest = path

        if j < 0:
            # support reverse indexing
            j += len(union.options)

        if j >= len(union.options) or j < 0:
            raise ValueError("Invalid path leading to non-existing branch.")

        new_opts = []

        for i, node in union.options:
            if i != j:
                new_opts.append(node.copy())
            elif rest:
                new_opts.append(self.visit(node, rest))

        return Union(new_opts)

    def visit_record(self, rec, path):
        assert path, "empty path is not valid"

        fname, *rest = path

        if fname not in rec.fields:
            raise ValueError(f"Invalid path leading to non-existing branch {fname}")

        fields = {}

        for name, node in rec.fields.items():
            if fname != name:
                fields[name] = node.copy()
            elif rest:
                fields[fname] = self.visit(node, rest)

        return Record(fields)

    def visit_tuple(self, tup, path):
        assert path, "empty path is not valid"

        j, *rest = path

        if j < 0:
            # support reverse indexing
            j += len(tup.fields)

        if j >= len(tup.fields) or j < 0:
            raise ValueError("Invalid path leading to non-existing branch.")

        fields = []

        for i, node in enumerate(tup.fields):
            if i != j:
                fields.append(node.copy())
            elif rest:
                fields.append(self.visit(node, rest))

        return Tuple(fields)
