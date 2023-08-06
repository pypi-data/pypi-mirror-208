from typing import TypeVar, Union

from cleanchausie.consts import OMITTED, omitted


def getter(dict_or_obj, field_name, default):
    if isinstance(dict_or_obj, dict):
        return dict_or_obj.get(field_name, default)

    return getattr(dict_or_obj, field_name, default)


T = TypeVar("T")
D = TypeVar("D")


def fallback(value: Union[T, OMITTED], default: D) -> Union[T, D]:
    """Return the value if it is not omitted, otherwise return the default."""
    if default is omitted:
        raise ValueError("The default cannot be `omitted`")

    if value is not omitted:
        return value

    return default
