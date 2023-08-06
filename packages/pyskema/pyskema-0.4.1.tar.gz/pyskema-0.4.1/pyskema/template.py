"Generate template data from a schema."

from .schema import AtomType
from .visitor import Visitor


def template(schema):
    "Generate a template from :code:`schema`"

    return Templater().template_node(schema)


class Templater(Visitor):
    """Visitor implementing templating.

    You should probably be using :func:`template` instead.
    """

    def template_node(self, value):
        data = self.visit(value)

        if value.optional:
            if isinstance(data, dict):
                data.update(value.default)
            elif isinstance(data, (float, int, str)):
                data = value.default

        return data

    def visit_tuple(self, tup):
        return [
            self.template_node(node)
            for node in tup.elements
        ]

    def visit_record(self, rec):
        return {
            key: self.template_node(node)
            for key, node in rec.fields.items()
        }

    def visit_union(self, union):
        return self.template_node(union.options[0])

    def visit_atom(self, atom):
        if atom.type_ == AtomType.OPTION:
            return f"... {atom.options}"
        elif atom.type_ == AtomType.BOOL:
            return "... bool"
        elif atom.type_ == AtomType.FLOAT:
            return "... float"
        elif atom.type_ == AtomType.INT:
            return "... int"
        elif atom.type_ == AtomType.STR:
            return "... string"

    def visit_map(self, map):
        return {
            "XX": self.template_node(map.element)
        }

    def visit_collection(self, collection):
        return [
            self.template_node(collection.element)
        ]
