import functools
from typing import Optional

import cleancat.base

from cleanchausie import Omittable
from cleanchausie.consts import omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, Nullability, Required, field
from cleanchausie.fields.utils import passthrough


def cleancat_field_bridge(
    f: cleancat.base.Field, nullability: Optional[Nullability] = None
) -> Field:
    """Create a cleanchausie field definition from a cleancat field."""

    @functools.wraps(f.clean)
    @passthrough((omitted,))
    def clean(*args, **kwargs):
        try:
            return f.clean(*args, **kwargs)
        except cleancat.base.ValidationError as e:
            return Error(msg=e.args and e.args[0])
        except cleancat.base.StopValidation as e:
            return e.args and e.args[0]

    # Cleancat fields are not really required if they have a
    # default, even if they have `required` set to True.
    nullability = nullability or (
        Required()
        if f.required and f.default is None
        else Omittable(omitted_value_factory=lambda: clean(None))
    )

    return field(clean, serialize_func=f.serialize, nullability=nullability)
