from typing import Any, Union

from cleanchausie.consts import EMPTY, empty, omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import noop, passthrough


def IntField(  # noqa: N802
    min_value: Union[EMPTY, int] = empty, max_value: Union[EMPTY, int] = empty
) -> Field[int]:
    @passthrough((None, omitted))
    def _intfield(value: Any) -> Union[int, Error]:
        """Simple string coercion/validation for int values."""
        # coerce from string if needed
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                return Error(msg="Unable to parse int from given string.")

        return Error(msg=f"Unhandled type '{type(value)}', could not coerce.")

    @passthrough((None, omitted))
    def _min(value: int) -> Union[int, Error]:
        if not isinstance(min_value, EMPTY) and value < min_value:
            return Error(
                msg=f"Value must be greater than or equal to {min_value}."
            )
        return value

    @passthrough((None, omitted))
    def _max(value: int) -> Union[int, Error]:
        if not isinstance(max_value, EMPTY) and value > max_value:
            return Error(
                msg=f"Value must be less than or equal to {max_value}."
            )
        return value

    return field(noop, parents=(_intfield, _min, _max))
