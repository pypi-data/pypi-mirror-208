from typing import Any, Type, TypeVar, Union

from cleanchausie.consts import omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough

T = TypeVar("T")


def InstanceField(of_type: Type[T]) -> Field[T]:  # noqa: N802
    @field
    @passthrough((None, omitted))
    def _instance_field(value: Any) -> Union[T, Error]:
        if isinstance(value, of_type):
            return value
        return Error(f"Expected an object of type {of_type.__name__}")

    return _instance_field
