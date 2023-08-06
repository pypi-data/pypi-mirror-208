from typing import Any, Union

from cleanchausie import omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough


def BoolField() -> Field[bool]:  # noqa: N802
    @field
    @passthrough((None, omitted))
    def _boolfield(value: Any) -> Union[bool, Error]:
        if not isinstance(value, bool):
            return Error(msg="Value is not a boolean.")
        return value

    return _boolfield
