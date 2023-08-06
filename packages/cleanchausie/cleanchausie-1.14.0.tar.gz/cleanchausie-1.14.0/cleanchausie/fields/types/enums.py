from enum import Enum
from typing import Any, Iterable, Type, TypeVar, Union

from cleanchausie.consts import EMPTY, empty, omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough

EnumCls = TypeVar("EnumCls", bound=Enum)


def EnumField(  # noqa: N802
    enum_cls: Type[EnumCls],
    valid_options: Union[Iterable[EnumCls], EMPTY] = empty,
) -> Field[EnumCls]:
    if not isinstance(valid_options, EMPTY):
        enforced_options = frozenset(valid_options)
    else:
        enforced_options = frozenset()

    @passthrough((None, omitted))
    def _enum_field(value: Any) -> Union[EnumCls, Error]:
        options = enforced_options if enforced_options else enum_cls
        # mypy doesn't let us express `EnumType[EnumCls]`, so it thinks there's
        # no `__iter__` on `enum_cls`
        option_strings = sorted([str(o.value) for o in options])  # type: ignore
        err_msg = f"Value must be one of: {', '.join(option_strings)}"
        try:
            enum_val = enum_cls(value)
        except (ValueError, TypeError):
            return Error(msg=err_msg)

        if enforced_options and enum_val not in enforced_options:
            return Error(msg=err_msg)

        return enum_val

    def _serialize(value: EnumCls) -> Any:
        return value.value

    return field(_enum_field, serialize_func=_serialize)
