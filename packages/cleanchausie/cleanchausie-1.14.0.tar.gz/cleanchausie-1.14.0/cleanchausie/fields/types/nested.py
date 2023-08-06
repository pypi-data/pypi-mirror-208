import inspect
from typing import TYPE_CHECKING, Any, Type, TypeVar, Union, overload

from typing_extensions import assert_never

from cleanchausie.consts import empty, omitted
from cleanchausie.errors import Errors, ValidationError
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough
from cleanchausie.schema_definition import SchemaDefinition

if TYPE_CHECKING:
    from cleanchausie.schema import Schema

T = TypeVar("T")
T_SCHEMA = TypeVar("T_SCHEMA", bound="Schema")


@overload
def NestedField(inner_schema: Type[T_SCHEMA]) -> Field[T_SCHEMA]:  # noqa: N802
    ...


@overload
def NestedField(inner_schema: SchemaDefinition[T]) -> Field[T]:  # noqa: N802
    ...


def NestedField(  # noqa: N802
    inner_schema: Union[Type[T_SCHEMA], SchemaDefinition[T]]
) -> Union[Field[T_SCHEMA], Field[T]]:
    from cleanchausie import Schema, clean, serialize

    schema_def: SchemaDefinition[T]
    if inspect.isclass(inner_schema) and issubclass(inner_schema, Schema):
        schema_def = inner_schema._schema_definition
    elif isinstance(inner_schema, SchemaDefinition):
        schema_def = inner_schema

    @passthrough((None, omitted))
    def _call(value: Any, context: Any = empty) -> Union[T, Errors]:
        result = clean(schema_def, value, context=context)
        if isinstance(result, ValidationError):
            return Errors(errors=result.errors)
        else:
            return result

        assert_never(result)

    return field(_call, serialize_func=serialize)
