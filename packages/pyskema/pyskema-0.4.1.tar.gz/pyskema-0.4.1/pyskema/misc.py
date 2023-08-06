"Miscellaneous utils."


def closest(alternatives, key):
    """Search among :code:`alternatives` the element to :code:`key`.

    Uses :func:`lev_dist` to compute the distance.

    :param alternatives: a :code:`list[str]` of elements to analyse.
    :param key: a :code:`str` key to search for.
    """
    return min(alternatives, key=lambda s: lev_dist(key, s))


def lev_dist(a, b):
    "Compute the Levenstein distance between two :code:`str`."

    len_a = len(a) + 1
    len_b = len(b) + 1

    if len_b > len_a:
        return lev_dist(b, a)

    prev = list(range(len_a))
    current = [0] * len_a

    for j in range(1, len_b):
        current[0] = j
        for i in range(1, len_a):
            if a[i - 1] == b[j - 1]:
                current[i] = prev[i - 1]  # mat[i, j] = mat[i - 1, j - 1]
            else:
                current[i] = min(  # mat[i, j] =
                    current[i - 1] + 1,  # deletion mat[i - 1, j] + 1
                    prev[i] + 1,  # insertion mat[i, j - 1]
                    prev[i - 1] + 1,  # substitution  mat[i - 1, j - 1]
                )

        # swap rows
        current, prev = prev, current

    return prev[-1]


class Result:
    "The Result monad."

    def __init__(self, valid: bool, val):
        if valid:
            self._value = val
            self._error = None
        else:
            self._value = None
            self._error = val

        self.valid = valid

    @classmethod
    def ok(cls, value):
        return cls(True, value)

    @classmethod
    def fail(cls, error):
        return cls(False, error)

    @property
    def value(self):
        assert self.valid, "Try to unwrap invalid result."
        return self._value

    @property
    def error(self):
        assert not self.valid, "Try to unwrap the error of a valid result."
        return self._error

    def __bool__(self):
        return self.valid
