import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Tuple,
    TypeVar,
    Union,
    overload,
)

import attrs

from cleanchausie.consts import empty
from cleanchausie.errors import Error, Errors, ValidationError

if TYPE_CHECKING:
    from cleanchausie.fields.field import Field
    from cleanchausie.fields.validation import Value

T = TypeVar("T")


def noop(value: T) -> T:
    return value


T_FUNC = TypeVar("T_FUNC", bound=Callable[..., Any])


def passthrough(values: Tuple[Any, ...]) -> Callable[[T_FUNC], T_FUNC]:
    """If any of the given values is encountered, skip the inner function.

    This is useful for defining reusable validation logic that doesn't handle
    `None` or `omitted` specially.

    The value checked is the `value` kwarg (if provided).
    """

    def _passthrough(fn):
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if "value" in kwargs and kwargs["value"] in values:
                return kwargs["value"]
            return fn(*args, **kwargs)

        return wrapper

    return _passthrough


@overload
def wrap_result(field: Tuple[Union[str, int], ...], result: Error) -> Error:
    ...


@overload
def wrap_result(
    field: Tuple[Union[str, int], ...], result: "Value"
) -> "Value":
    ...


def wrap_result(
    field: Tuple[Union[str, int], ...], result: Any
) -> Union["Value", Error]:
    from cleanchausie.fields.validation import Value

    if isinstance(result, Error):
        return attrs.evolve(result, field=field + result.field)
    elif not isinstance(result, Value):
        return Value(value=result)
    return result


def clean_field(
    field: "Field[T]", data: Any, context: Any = empty
) -> Union[T, ValidationError]:
    """Validate data using a specific field.

    This can be helpful for defining reusable fields, or for using complex
    fields as top-level schemas as well.
    """
    from cleanchausie.fields.validation import validate_field

    result = validate_field(
        field=field,
        path=(),
        root_value=data,
        value=data,
        context=context,
        intermediate_results={},
    )
    if isinstance(result, Errors):
        return ValidationError(result.flatten())
    return result.value


def serialize_field(field: "Field[T]", value: T) -> Any:
    """Serialize a value using a specific field.

    It's assumed that the value has already been validated.
    """
    return field.serialize_func(value)
