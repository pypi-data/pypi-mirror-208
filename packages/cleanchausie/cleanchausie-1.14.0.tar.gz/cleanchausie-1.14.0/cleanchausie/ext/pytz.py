from typing import Union

import pytz
from pytz import BaseTzInfo

from cleanchausie.consts import OMITTED, omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough


def PytzTimezoneField() -> Field[BaseTzInfo]:  # noqa: N802
    def _serialize_fn(
        value: Union[BaseTzInfo, OMITTED, None],
    ) -> Union[str, OMITTED, None]:
        if not isinstance(value, BaseTzInfo):
            return value
        return value.tzname(None)

    @field(serialize_func=_serialize_fn)
    @passthrough((None, omitted))
    def _pytz_timezone_field(value: str) -> Union[BaseTzInfo, Error]:
        try:
            return pytz.timezone(value)
        except pytz.UnknownTimeZoneError:
            return Error(msg=f"Unknown timezone: {value}")

    return _pytz_timezone_field
