"Implement validation of data against a schema."

from dataclasses import dataclass
from typing import List


from .schema import AtomType, Atom, Node, Record, Collection
from .visitor import Visitor
from .misc import closest, Result


def validate(data, schema, fail=True):
    """Validate a piece of data against a schema.

    :param data: a piece of data to validate.
    :param schema: a schema to refer to
    :param fail: (optional, :code:`True`)

        - if :code:`True`, raise an :class:`InvalidDataError` when failing to validate data
        - else, return None
    """
    assert isinstance(schema, Node), f"schema should be a Node instance, not {schema}."

    r = Validator.validate(schema, data)

    if r.valid:
        return r.value
    elif fail:
        raise InvalidDataError(r.error)

    return None


class Validator(Visitor):
    """Visitor implementing validation.

    You should probably be using :func:`validate` instead.
    """

    @classmethod
    def validate(cls, schema, data):
        """validate data against schema.

        :param schema: instance of Node
        :param data: the data to validate
        """
        return cls().visit(schema, data)

    def visit_atom(self, atom, data) -> Result:
        if atom.type_ == AtomType.INT:
            if isinstance(data, int):
                return Result.ok(data)
            elif isinstance(data, float):
                if int(data) == data:
                    return Result.ok(int(data))

        elif atom.type_ == AtomType.FLOAT:
            if isinstance(data, (float, int)):
                return Result.ok(float(data))

        elif atom.type_ == AtomType.STR:
            if isinstance(data, str):
                return Result.ok(data)

        elif atom.type_ == AtomType.OPTION:
            assert atom.options is not None, "atom.options must be set"
            if isinstance(data, str) and data in atom.options:
                return Result.ok(data)

        elif atom.type_ == AtomType.BOOL:
            if isinstance(data, bool):
                return Result.ok(data)

        else:
            raise NotImplementedError(f"{atom.type_} is not supported yet.")

        # invalid atom
        return Result.fail(
            Mismatch(
                [],
                data,
                f"{repr(data)} is not a valid {atom.type_.name(atom.options)}.",
            )
        )

    def visit_union(self, union, data) -> Result:
        errors = []
        for op in union.options:
            m = self.visit(op, data)
            if m.valid:
                # success at first match
                return Result.ok((op, m.value))
            else:
                errors.append(m.error)

        # no valid option
        return Result.fail(
            Mismatch(
                [],
                data,
                f"{repr(data)} does not validate any of the valid alternatives:\n"
                + "\n".join("- " + error_message(err, no_loc=True) for err in errors),
            )
        )

    def visit_record(self, rec, data) -> Result:
        try:
            pairs = data.items()
        except AttributeError:
            # early return because we cannot go further anyway
            return Result.fail(
                Mismatch([], data, f"{repr(data)} does not implement the items method.")
            )

        got = set()
        res = {}
        errors = []

        for key, value in pairs:
            if key not in rec.fields:
                other = closest(rec.fields.keys(), key)
                errors.append(
                    Mismatch([], data, f"{key} is not a valid member of this record. Did you mean {other}")
                )
                continue

            m = self.visit(rec.fields[key], value)
            if m.valid:
                got.add(key)
                res[key] = m.value
            else:
                errors.append(m.error.from_(key))

        for key in set(rec.fields.keys()).difference(got):
            if not rec.fields[key].optional:
                # collect missing members
                errors.append(Mismatch([], data, f"{key} is missing."))
            else:
                default = rec.fields[key].default
                r = self.visit(rec.fields[key], default)
                if not r.valid:
                    return Result.fail(
                        Mismatch([key], default, "Default value is invalid data.")
                    )
                res[key] = r.value

        if errors:
            return Result.fail(Mismatches(errors))
        else:
            return Result.ok(res)

    def visit_tuple(self, tup, data) -> Result:
        try:
            elements = list(data)
        except TypeError:
            # early return because we cannot go further anyway
            return Result.fail(Mismatch([], data, f"{repr(data)} is not iterable."))

        res = []
        errors = []

        if len(elements) != len(tup.fields):
            errors.append(
                Mismatch(
                    [],
                    data,
                    f"Expected {len(tup.fields)} elements, but got {len(elements)}.",
                )
            )

        for i, (schema, value) in enumerate(zip(tup.fields, elements)):
            m = self.visit(schema, value)
            if m.valid:
                res.append(m.value)
            else:
                errors.append(m.error.from_(str(i)))

        if errors:
            return Result.fail(Mismatches(errors))
        else:
            return Result.ok(res)

    def visit_collection(self, collection, data) -> Result:
        if isinstance(data, str):
            return Result.fail(Mismatch([], data, f"{repr(data)} is a string, not a collection"))

        try:
            col = list(data)
        except AttributeError:
            return Result.fail(Mismatch([], data, f"{repr(data)} is not iterable."))

        validate = []
        errors = []

        for i, e in enumerate(col):
            m = self.visit(collection.element, e)
            if m.valid:
                validate.append(m.value)
            else:
                # collect mismatches in elements
                errors.append(m.error.from_(str(i)))

        if errors:
            return Result.fail(Mismatches(errors))
        else:
            return Result.ok(validate)

    def visit_map(self, map_, data) -> Result:
        try:
            pairs = data.items()
        except AttributeError:
            return Result.fail(
                Mismatch([], data, f"{repr(data)} does not implement the items method.")
            )

        res = {}
        errors = []

        for key, value in pairs:
            m = self.visit(map_.element, value)
            if m.valid:
                res[key] = m.value
            else:
                # collect mismatches in elements
                errors.append(m.error.from_(key))

        if errors:
            return Result.fail(Mismatches(errors))
        else:
            return Result.ok(res)


@dataclass
class Mismatch:
    "Infos on a mismatch between the schema and a piece of data."

    where: List[str]
    what: object
    why: str

    def from_(self, where):
        return Mismatch([where, *self.where], self.what, self.why)


class Mismatches:
    "A collection of mismatches between schema and data."

    def __init__(self, errors):
        self.errors = []

        for err in errors:
            if isinstance(err, Mismatches):
                self.errors.extend(err.errors)
            else:
                self.errors.append(err)

    def from_(self, where):
        return Mismatches([e.from_(where) for e in self.errors])


class InvalidDataError(ValueError):
    "Exception signaling failure to validate data."

    def __init__(self, mismatch):
        super().__init__(error_message(mismatch))


def error_message(mismatch, no_loc=False):
    "Format the error message for :class:`InvalidDataError`."
    if isinstance(mismatch, Mismatches):
        msg = []
        for mism in mismatch.errors:
            msg.append(error_message(mism, no_loc=no_loc))

        return "\n".join(msg)
    elif no_loc:
        return mismatch.why
    else:
        if None:
            location = ".".join(mismatch.where)
        else:
            location = "[toplevel]"

        return f"In {location}: {mismatch.why}"
