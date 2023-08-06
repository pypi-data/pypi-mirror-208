from typing import Any, Tuple, Union

from typing_extensions import assert_never

from cleanchausie.consts import empty, omitted
from cleanchausie.errors import Error, Errors
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough
from cleanchausie.fields.validation import validate_field


def TupleField(  # noqa: N802
    inner_fields: Union[Field, Tuple[Field, ...]]
) -> Field[Tuple]:
    @passthrough((None, omitted))
    def _call(
        value: Any, root_value, intermediate_results, context=empty
    ) -> Union[Tuple, Error, Errors]:
        result = _impl(value)
        if not isinstance(result, (Error, Errors)):
            if isinstance(inner_fields, Field):
                inner_results = [
                    validate_field(
                        field=inner_fields,
                        path=(idx,),
                        root_value=root_value,
                        value=inner_value,
                        context=context,
                        intermediate_results=intermediate_results,
                    )
                    for idx, inner_value in enumerate(value)
                ]
            elif isinstance(inner_fields, tuple):
                if len(value) != len(inner_fields):
                    return Error(
                        msg=f"Expected {len(inner_fields)} items, got {len(value)}."
                    )

                inner_results = [
                    validate_field(
                        field=inner_fields[idx],
                        path=(idx,),
                        root_value=root_value,
                        value=inner_value,
                        context=context,
                        intermediate_results=intermediate_results,
                    )
                    for idx, inner_value in enumerate(value)
                ]
            else:
                assert_never(inner_fields)

            flattened_errors = []
            for r in inner_results:
                if isinstance(r, Errors):
                    flattened_errors.extend(r.flatten())
            if flattened_errors:
                return Errors(errors=flattened_errors)
            else:
                # construct result with the validated inner data
                result = tuple(
                    v.value for v in inner_results if not isinstance(v, Errors)
                )
        return result

    def _impl(value: Any) -> Union[Tuple, Error]:
        if isinstance(value, list):
            value = tuple(value)

        if isinstance(value, tuple):
            return value

        return Error(msg="Unhandled type")

    return field(_call)
