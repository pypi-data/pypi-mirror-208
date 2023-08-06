import inspect
import itertools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    List,
    Optional as T_Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

import attr

from cleanchausie.consts import OMITTED, omitted
from cleanchausie.errors import Error, Errors
from cleanchausie.fields.utils import noop

if TYPE_CHECKING:
    from cleanchausie.fields.validation import UnvalidatedMappedValue


class Nullability:
    allow_none: bool


@attr.frozen
class Required(Nullability):
    allow_none: bool = False


@attr.frozen
class Omittable(Nullability):
    allow_none: bool = True
    omitted_value_factory: Union[OMITTED, Callable] = omitted
    omitted_value: Any = omitted


FieldReturnType = TypeVar("FieldReturnType")


@attr.frozen
class Field(Generic[FieldReturnType]):
    validators: Tuple[Callable, ...]
    """Callable that validate a the given field's value."""

    accepts: T_Optional[Tuple[str, ...]]
    """Field names accepted when parsing unvalidated input.

    If left unspecified, defaults to the name of the attribute defined on the
    schema. It can be explicitly set to `None` to force the schema to not
    accept any input. This can be useful for validation-only fields or derived
    fields.
    """

    serialize_to: T_Optional[str]
    """If provided overrides the name of the field during serialization."""

    serialize_func: Callable[[Any], Any]
    """Used when serializing this field. Defaults to a noop passthrough."""

    nullability: Nullability

    depends_on: Tuple[str, ...]
    """Other fields on the same schema this field depends on"""

    # lets mypy and IDE's autocomplete/resolve to the right type
    def __get__(self, instance, owner) -> FieldReturnType:  # type: ignore[empty-body]
        ...


# to avoid func calls in args. Effectively the same thing, but required is
# not mutable, so it shouldn't matter.
required = Required()


FType = TypeVar("FType")
ParentsAnnotation = Union[
    Union[Callable, Field[Any]], Tuple[Union[Callable, Field[Any]], ...]
]


# when decorating a function (decorated func is passed to the inner func)
@overload
def field(
    *,
    parents: ParentsAnnotation = (),
    accepts: T_Optional[Tuple[str, ...]] = (),
    serialize_to: T_Optional[str] = None,
    serialize_func: T_Optional[Callable] = None,
    nullability: Nullability = required,
) -> Callable[
    [
        Union[
            Callable[
                ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
            ],
            Callable[..., FType],
        ]
    ],
    Field[FType],
]:
    ...


# defining simple fields with existing functions
@overload
def field(
    decorated_func: Callable[
        ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
    ],
    *,
    parents: ParentsAnnotation = (),
    accepts: T_Optional[Tuple[str, ...]] = (),
    serialize_to: T_Optional[str] = None,
    serialize_func: T_Optional[Callable] = None,
    nullability: Nullability = required,
) -> Field[FType]:
    ...


@overload
def field(
    decorated_func: Field[FType],
    *,
    parents: ParentsAnnotation = (),
    accepts: T_Optional[Tuple[str, ...]] = (),
    serialize_to: T_Optional[str] = None,
    serialize_func: T_Optional[Callable] = None,
    nullability: Nullability = required,
) -> Field[T_Optional[FType]]:
    ...


def field(
    decorated_func: T_Optional[
        Union[
            Callable[
                ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
            ],
            Field[FType],
        ]
    ] = None,
    *,
    parents: ParentsAnnotation = (),
    accepts: T_Optional[Tuple[str, ...]] = (),
    serialize_to: T_Optional[str] = None,
    serialize_func: T_Optional[Callable] = None,
    nullability: Nullability = required,
) -> Union[
    Callable[
        [
            Union[
                Callable[
                    ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
                ],
                Callable[..., FType],
            ]
        ],
        Field[FType],
    ],
    Field[FType],
    Field[T_Optional[FType]],
]:
    """Defines a Field.

    Args:
        decorated_func: The only accepted positional arg, must be either a
            callable or a `Field` instance.
        parents: Optionally a tuple of any parent fields. Validated values chain between
            parents in order they've been given here, before being passed to this
            field's validation function. Note that if a `Field` is given instead of a
            `Callable`, only the validators are reused.
        accepts: Optionally a tuple of field names to accept values from. If not given,
            defaults to the field name on the schema. Field names given first are given
            precedent. Can be set to an explicit `None` to signal no value should
            be accepted for this field.
        serialize_to: The field name to serialize to. Defaults to the field name on the
            schema.
        serialize_func: Optionally a function that transforms the serialized value
            during serialization. Defaults to noop, which passes through the value
            unchanged.
        nullability: An instance of one of `Nullability`'s descendants, used to define
            behavior if a field is omitted or falsy. Defaults to Required.
    """
    # make it a little more convenient for cases where there's only one parent
    wrapped_parents = parents if isinstance(parents, tuple) else (parents,)

    if decorated_func is not None:
        if isinstance(decorated_func, Field):
            return _outer_field(
                inner_func=noop,
                parents=wrapped_parents + (decorated_func,),
                accepts=accepts,
                serialize_to=serialize_to,
                serialize_func=(
                    serialize_func or decorated_func.serialize_func
                ),
                nullability=nullability,
            )
        else:
            return _outer_field(
                inner_func=decorated_func,
                parents=wrapped_parents,
                accepts=accepts,
                serialize_to=serialize_to,
                serialize_func=serialize_func or noop,
                nullability=nullability,
            )

    else:

        def _wrap(
            inner_func: Callable[
                ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
            ]
        ) -> Field[FType]:
            return _outer_field(
                inner_func,
                parents=wrapped_parents,
                accepts=accepts,
                serialize_to=serialize_to,
                serialize_func=serialize_func or noop,
                nullability=nullability,
            )

        return _wrap


def _outer_field(
    inner_func: Callable[
        ..., Union[Error, Errors, "UnvalidatedMappedValue", FType]
    ],
    *,
    parents: Tuple[Union[Callable, Field], ...] = (),
    accepts: T_Optional[Tuple[str, ...]] = (),
    serialize_to: T_Optional[str] = None,
    serialize_func: Callable = noop,
    nullability: Nullability = required,
) -> Field[FType]:
    # flatten any parents defined as fields
    validators: List[Callable] = []
    for p in parents + (inner_func,):
        if isinstance(p, Field):
            validators.extend(p.validators)
        else:
            validators.append(p)

    # find any declared dependencies on other fields
    deps = {
        n
        for n in itertools.chain(
            *[inspect.signature(f).parameters.keys() for f in validators]
        )
        if n not in {"context", "value", "root_value", "intermediate_results"}
    }
    f: Field[FType] = Field(
        nullability=nullability,
        validators=tuple(validators),
        accepts=accepts,
        serialize_to=serialize_to,
        serialize_func=serialize_func,
        depends_on=tuple(deps),
    )
    return f
