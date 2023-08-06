import functools
import inspect
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Optional as T_Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import attr

from cleanchausie.consts import empty, omitted
from cleanchausie.errors import Error, Errors
from cleanchausie.fields.field import Field, Omittable, Required

T = TypeVar("T")
V = TypeVar("V")


@attr.frozen
class Value(Generic[T]):
    value: T


@attr.frozen
class UnvalidatedWrappedValue(Generic[T, V]):
    value: Collection[V]
    inner_field: "Field[T]"

    construct: Callable
    """Called to construct the wrapped type with validated data."""


UnvalidatedMappedKeyType = TypeVar("UnvalidatedMappedKeyType")
UnvalidatedMappedValueType = TypeVar("UnvalidatedMappedValueType")


@attr.frozen
class UnvalidatedMappedValue(
    Generic[UnvalidatedMappedKeyType, UnvalidatedMappedValueType]
):
    value: Dict
    key_field: T_Optional["Field[UnvalidatedMappedKeyType]"]
    value_field: T_Optional["Field[UnvalidatedMappedValueType]"]

    construct: Callable
    """Called to construct the mapping type with validated data."""


def _get_deps(func: Callable) -> Set[str]:
    return set(inspect.signature(func).parameters.keys())


def inject_deps(
    func: Callable,
    val: Any,
    context: Any,
    intermediate_results: Dict[str, Any],
    root_value: Any,
) -> Callable:
    deps = _get_deps(func)
    if not deps:
        return func

    # an empty context default value means its optional/passthrough
    if (
        "context" in deps
        and context is empty
        and inspect.signature(func).parameters["context"].default is not empty
    ):
        raise ValueError("Context is required for evaluating this schema.")

    return functools.partial(
        func,
        **{
            dep: v.value
            for dep, v in intermediate_results.items()
            if dep in deps
        },
        **{
            dep: v
            for dep, v in {
                "context": context,
                "value": val,
                "root_value": root_value,
                "intermediate_results": intermediate_results,
            }.items()
            if dep in deps
        },
    )


def validate_wrapped_value_result(
    result: UnvalidatedWrappedValue,
    root_value: Any,
    context: Any,
    intermediate_results: Dict[str, Any],
) -> Union[Value, Errors]:
    inner_results = [
        result.inner_field.run_validators(
            field=(idx,),
            root_value=root_value,
            value=inner_value,
            context=context,
            intermediate_results=intermediate_results,
        )
        for idx, inner_value in enumerate(result.value)
    ]
    flattened_errors = []
    for r in inner_results:
        if isinstance(r, Errors):
            flattened_errors.extend(r.flatten())
    if flattened_errors:
        return Errors(errors=flattened_errors)

    # construct result with the validated inner data
    return result.construct(inner_results)


def validate_mapped_value_result(
    result: UnvalidatedMappedValue,
    root_value: Any,
    context: Any,
    intermediate_results: Dict[str, Any],
) -> Union[Value, Errors]:
    if result.key_field:
        key_results = [
            validate_field(
                field=result.key_field,
                path=(f"{key} (key)",),
                root_value=root_value,
                value=key,
                context=context,
                intermediate_results=intermediate_results,
            )
            for key in result.value.keys()
        ]
    else:
        key_results = [Value(k) for k in result.value.keys()]

    if result.value_field:
        value_results = [
            validate_field(
                field=result.value_field,
                path=(f"{key} (value)",),
                root_value=root_value,
                value=value,
                context=context,
                intermediate_results=intermediate_results,
            )
            for key, value in result.value.items()
        ]
    else:
        value_results = [Value(v) for v in result.value.values()]

    flattened_errors = []
    for r in key_results + value_results:
        if isinstance(r, Errors):
            flattened_errors.extend(r.flatten())
    if flattened_errors:
        return Errors(errors=flattened_errors)

    # construct result with the validated key/value pairs
    return result.construct(tuple(zip(key_results, value_results)))


def validate_field(
    field: "Field[T]",
    path: Tuple[Union[str, int], ...],
    root_value: Any,
    value: Any,
    context: Any,
    intermediate_results: Dict[str, Any],
) -> Union["Value[T]", Errors]:
    from cleanchausie.fields.utils import wrap_result

    # handle nullability
    if value in (omitted, None) and any(
        ("value" in _get_deps(v) for v in field.validators)
    ):
        if value is None and not field.nullability.allow_none:
            if isinstance(field.nullability, Required):
                msg = "This field is required, and must not be None."
            else:
                msg = "This field must not be None."

            return Errors(field=path, errors=[Error(msg=msg)])
        elif value is omitted and isinstance(field.nullability, Required):
            return Errors(
                field=path, errors=[Error(msg="This field is required.")]
            )
        elif value is omitted and isinstance(field.nullability, Omittable):
            value = (
                field.nullability.omitted_value_factory()
                if field.nullability.omitted_value_factory is not omitted
                else field.nullability.omitted_value
            )

    result = value
    for validator in field.validators:
        result = inject_deps(
            func=validator,
            val=result,
            context=context,
            intermediate_results=intermediate_results,
            root_value=root_value,
        )()
        if isinstance(result, UnvalidatedWrappedValue):
            result = validate_wrapped_value_result(
                result=result,
                root_value=root_value,
                context=context,
                intermediate_results=intermediate_results,
            )
        elif isinstance(result, UnvalidatedMappedValue):
            result = validate_mapped_value_result(
                result=result,
                root_value=root_value,
                context=context,
                intermediate_results=intermediate_results,
            )

        if isinstance(result, (Error, Errors)):
            if field.accepts is None and not result.field:
                # ignore the last part of the path if this field isn't
                # directly based on any input field
                err_field = path[:-1]
            else:
                err_field = result.field or path

            if isinstance(result, Errors):
                errors = result.flatten()
            else:
                errors = [Error(msg=result.msg)]
            return Errors(field=err_field, errors=errors)

    return wrap_result(field=path, result=result)
