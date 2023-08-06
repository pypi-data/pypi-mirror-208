from typing import Dict, List, Tuple, Union

import attr


@attr.frozen
class ValidationError:
    errors: List["Error"]

    def serialize(self) -> Dict:
        """Serialize field-level errors dict.

        This is useful for rest responses and test assertions.
        """
        return {
            "errors": [{"msg": e.msg, "field": e.field} for e in self.errors]
        }


@attr.frozen
class Error:
    msg: str
    field: Tuple[Union[str, int], ...] = ()


@attr.frozen
class Errors:
    errors: List[Error]
    field: Tuple[Union[str, int], ...] = ()

    def flatten(self) -> List[Error]:
        from .fields.utils import wrap_result

        return [
            wrap_result(field=self.field, result=err) for err in self.errors
        ]
