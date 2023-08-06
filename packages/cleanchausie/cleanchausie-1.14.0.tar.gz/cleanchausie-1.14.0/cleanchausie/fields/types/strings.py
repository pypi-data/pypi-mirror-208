import re
from typing import Any, Union

from cleanchausie.consts import EMPTY, empty, omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import noop, passthrough


def StrField(  # noqa: N802
    trim: bool = False,
    min_length: Union[EMPTY, int] = empty,
    max_length: Union[EMPTY, int] = empty,
) -> Field[str]:
    """Simple validation for str values.

    Args:
        trim: If True, the value will be stripped of leading and trailing
            whitespace. This is done before length validation.
        min_length: The minimum length of the string.
        max_length: The maximum length of the string.
    """

    @passthrough((None, omitted))
    def _strfield(value: Any) -> Union[str, Error]:
        if isinstance(value, str):
            return value

        return Error(msg=f"Expected a string, got '{type(value).__name__}'.")

    @passthrough((None, omitted))
    def _trim(value: str) -> str:
        if trim:
            return value.strip()
        return value

    @passthrough((None, omitted))
    def _min(value: str) -> Union[str, Error]:
        if not isinstance(min_length, EMPTY) and len(value) < min_length:
            return Error(
                msg=f"Length must be greater than or equal to {min_length}."
            )
        return value

    @passthrough((None, omitted))
    def _max(value: str) -> Union[str, Error]:
        if not isinstance(max_length, EMPTY) and len(value) > max_length:
            return Error(
                msg=f"Length must be less than or equal to {max_length}."
            )
        return value

    return field(noop, parents=(_strfield, _trim, _min, _max))


def RegexField(regex: str, flags: int = 0) -> Field[str]:  # noqa: N802
    _compiled_regex = re.compile(regex, flags)

    @passthrough((None, omitted))
    def _validate_regex(value: str) -> Union[str, Error]:
        if not _compiled_regex.match(value):
            return Error(msg="Invalid input.")
        return value

    return field(_validate_regex, parents=(StrField(),))


def URLField(  # noqa: N802
    require_tld=True,
    default_scheme=None,
    allowed_schemes=None,
    disallowed_schemes=None,
) -> Field[str]:
    def normalize_scheme(sch):
        if sch.endswith("://") or sch.endswith(":"):
            return sch
        return sch + "://"

    # FQDN validation similar to https://github.com/chriso/validator.js/blob/master/src/lib/isFQDN.js

    # ff01-ff5f -> full-width chars, not allowed
    alpha_numeric_and_symbols_ranges = "0-9a-z\u00a1-\uff00\uff5f-\uffff"

    tld_part = (
        require_tld
        and r"\.[{}-]{{2,63}}".format(alpha_numeric_and_symbols_ranges)
        or ""
    )
    scheme_part = "[a-z]+://"
    if default_scheme:
        default_scheme = normalize_scheme(default_scheme)
    scheme_regex = re.compile("^" + scheme_part, re.IGNORECASE)
    if default_scheme:
        scheme_part = f"({scheme_part})?"
    regex = r"^{}([-{}@:%%_+.~#?&/\\=]{{1,256}}{}|([0-9]{{1,3}}\.){{3}}[0-9]{{1,3}})(:[0-9]+)?([/?].*)?$".format(
        scheme_part, alpha_numeric_and_symbols_ranges, tld_part
    )
    regex_flags = re.IGNORECASE | re.UNICODE

    def compile_schemes_to_regexes(schemes):
        return [
            re.compile("^" + normalize_scheme(sch) + ".*", re.IGNORECASE)
            for sch in schemes
        ]

    allowed_schemes = allowed_schemes or []
    allowed_schemes_regexes = compile_schemes_to_regexes(allowed_schemes)

    disallowed_schemes = disallowed_schemes or []
    disallowed_schemes_regexes = compile_schemes_to_regexes(disallowed_schemes)

    @field(parents=(RegexField(regex=regex, flags=regex_flags),))
    @passthrough((None, omitted))
    def _urlfield(value: str) -> Union[Error, str]:
        if not scheme_regex.match(value):
            value = default_scheme + value

        if allowed_schemes:
            if not any(
                allowed_regex.match(value)
                for allowed_regex in allowed_schemes_regexes
            ):
                allowed_schemes_text = " or ".join(allowed_schemes)
                return Error(
                    msg=(
                        "This URL uses a scheme that's not allowed. You can only "
                        f"use {allowed_schemes_text}."
                    )
                )

        if disallowed_schemes:
            if any(
                disallowed_regex.match(value)
                for disallowed_regex in disallowed_schemes_regexes
            ):
                return Error(msg="This URL uses a scheme that's not allowed.")

        return value

    return _urlfield


def EmailField(max_length=254) -> Field[str]:  # noqa: N802
    email_regex = (
        r"^(?:[^\.@\s]|[^\.@\s]\.(?!\.))*[^.@\s]@"
        r"[^.@\s](?:[^\.@\s]|\.(?!\.))*\.[a-z]{2,63}$"
    )
    regex_flags = re.IGNORECASE

    @passthrough((None, omitted))
    def _email_field(value: str) -> Union[str, Error]:
        # trim any leading/trailing whitespace before validating the email
        ret = value.strip()

        # only allow up to max_length
        if len(ret) > max_length:
            return Error(f"Email exceeds max length of {max_length}")

        return ret

    return field(
        noop,
        parents=(
            StrField(),
            _email_field,
            RegexField(regex=email_regex, flags=regex_flags),
        ),
    )
