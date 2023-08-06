from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Type,
    TypeVar,
    Union,
)

import attr

from cleanchausie.consts import EMPTY, empty, omitted
from cleanchausie.errors import Error, Errors, ValidationError
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough
from cleanchausie.utils import getter

if TYPE_CHECKING:
    from cleanchausie.schema import Schema


def PolymorphicField(  # noqa: N802
    type_field: str,
    type_map: Dict[Any, Type["Schema"]],
    default_type_key: Any = empty,
) -> Field:
    """Map to different schemas based on a tagged type.

    This is useful for cases where different incompatible structures may be
    used, and which structure to validate against is tagged explicitly by a
    field.

    For example, we may want to validate "foo" and "bar" type items
    differently:
        [{"type": "foo", "foo": "bar"}, {"type": "bar", "bar": 1}]

    This would be possible with a field like:
        List(
            PolymorphicField(
                type_field="type",
                type_map={
                    "foo": Schema({"foo": Str()}),
                    "bar": Schema({"bar": Int()}),
                },
            )
        )

    Args:
        type_field: The field name that contains the type tag.
        type_map: A mapping of type tags to schemas.
        default_type_key: The default type tag to use if the type field is
            omitted.
    """
    from cleanchausie import clean

    @field
    @passthrough((None, omitted))
    def _polymorphic_field(
        value: Any, context: Any = empty
    ) -> Union["Schema", Errors]:
        type_val = getter(value, type_field, omitted)
        if type_val is omitted:
            if default_type_key is not empty:
                type_val = default_type_key
            else:
                # nested object does not have the type field
                return Errors(
                    errors=[
                        Error(
                            f"Required type field '{type_field}' not provided"
                        )
                    ]
                )

        inner_schema = type_map.get(type_val, empty)
        if isinstance(inner_schema, EMPTY):
            return Errors(errors=[Error(f"Type '{type_val}' is not handled.")])

        result = clean(inner_schema, value, context=context)
        if isinstance(result, ValidationError):
            return Errors(errors=result.errors)
        elif isinstance(result, inner_schema):
            return result

        raise TypeError

    return _polymorphic_field


T_COVARIANT = TypeVar("T_COVARIANT", covariant=True)


@attr.frozen
class PolySchemaMapping(Generic[T_COVARIANT]):
    public_type: str
    internal_type: Type[T_COVARIANT]
    serializer: Callable[[T_COVARIANT], Dict]
    clean: Callable[[Any, Any], Union[T_COVARIANT, ValidationError]]


T = TypeVar("T")


def SerializablePolymorphicField(  # noqa: N802
    type_field: str,
    mappings: Iterable[PolySchemaMapping[T]],
    default_type_key: Any = empty,
) -> Field[T]:
    """Similar to PolymorphicField, but also supports serialization.

    This is useful for cases where different incompatible structures may be
    used, and which structure to validate against is tagged explicitly by a
    field.

    As part of supporting more advanced serialization and parsing, the end
    result for validated values will generally be an instance of an internal
    type rather than of a schema. As such, explicit `internal_type`,
    `factory`, and `serializer` functions must be provided for each mapping.

    For example, we may want to validate "foo" and "bar" type items to
    internal types Foo and Bar, respectively:
        [{"type": "foo", "foo": "bar"}, {"type": "bar", "bar": 1}]

    This would be possible with a field like:
        SerializablePolymorphicField(
            type_field="type",
            mappings=[
                PolySchemaMapping(
                    public_type="foo",
                    internal_type=Foo,
                    schema_cls=Schema({"foo": Str()}),
                    serializer=lambda foo: {"foo": foo.foo},
                    factory=lambda schema: Foo(foo=schema.foo),
                ),
                PolySchemaMapping(
                    public_type="bar",
                    internal_type=Bar,
                    schema_cls=Schema({"bar": Int()}),
                    serializer=lambda bar: {"bar": bar.bar},
                    factory=lambda schema: Bar(bar=schema.bar),
                ),
            ],
        )

    Args:
        type_field: The field name that contains the type tag.
        mappings: A list of PolySchemaMapping's that link public type tags,
            schemas, and internal types.
        default_type_key: The default type tag to use if the type field is
            omitted.
    """

    def _get_mapping(public_type: str) -> Union[PolySchemaMapping[T], EMPTY]:
        return next(
            (m for m in mappings if m.public_type == public_type), empty
        )

    def _serialize_func(value):
        if value in (None, omitted):
            return value
        mapping = next(
            (m for m in mappings if isinstance(value, m.internal_type)),
            None,
        )
        if mapping is None:
            raise TypeError(
                f"Value '{value}' is not an instance of any of the "
                "provided mappings' internal types."
            )
        result = mapping.serializer(value)
        if isinstance(result, dict):
            result[type_field] = mapping.public_type
        return result

    @field(serialize_func=_serialize_func)
    @passthrough((None, omitted))
    def _polymorphic_field(
        value: Any, context: Any = empty
    ) -> Union["T", Errors]:
        type_val = getter(value, type_field, omitted)
        if type_val is omitted:
            if default_type_key is not empty:
                type_val = default_type_key
            else:
                # nested object does not have the type field
                return Errors(
                    errors=[
                        Error(
                            f"Required type field '{type_field}' not provided"
                        )
                    ]
                )

        mapping = _get_mapping(type_val)
        if isinstance(mapping, EMPTY):
            return Errors(errors=[Error(f"Type '{type_val}' is not handled.")])

        result = mapping.clean(value, context)
        if isinstance(result, ValidationError):
            return Errors(errors=result.errors)
        elif isinstance(result, mapping.internal_type):
            return result

        raise TypeError

    return _polymorphic_field
