import enum
from typing import Literal


class _OMITTED(enum.Enum):
    """
    A singleton for representing omitted values in validation.

    Written in a way mypy can parse. See
    https://www.python.org/dev/peps/pep-0484/#support-for-singleton-types-in-unions
    for more details.
    """

    token = "omitted"


# Use this to indicate a difference between None and omitted value.
OMITTED = Literal[_OMITTED.token]
omitted: OMITTED = _OMITTED.token


class EMPTY:
    """used as singleton for omitted options/kwargs"""

    def __repr__(self) -> str:
        return "empty"

    def __str__(self) -> str:
        return "empty"


empty = EMPTY()
