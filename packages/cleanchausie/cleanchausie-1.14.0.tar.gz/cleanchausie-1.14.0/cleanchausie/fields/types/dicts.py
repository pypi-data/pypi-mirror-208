from typing import (
    Any,
    Dict,
    List,
    Optional as T_Optional,
    Tuple,
    TypeVar,
    Union,
)

from cleanchausie.consts import omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough
from cleanchausie.fields.validation import UnvalidatedMappedValue, Value

DictKeyType = TypeVar("DictKeyType")
DictValueType = TypeVar("DictValueType")


def DictField(  # noqa: N802
    key_field: T_Optional[Field[DictKeyType]],
    value_field: T_Optional[Field[DictValueType]],
) -> "Field[Dict[DictKeyType, DictValueType]]":
    def construct(
        mapped_pairs: List[Tuple[Value, Value]]
    ) -> Dict[DictKeyType, DictValueType]:
        return {k.value: v.value for k, v in mapped_pairs}

    @passthrough((None, omitted))
    def _dict_field(
        value: Any,
    ) -> Union[UnvalidatedMappedValue[DictKeyType, DictValueType], Error]:
        if not isinstance(value, dict):
            return Error("Value is not a dictionary")
        return UnvalidatedMappedValue(
            value=value,
            key_field=key_field,
            value_field=value_field,
            construct=construct,
        )

    return field(_dict_field)
