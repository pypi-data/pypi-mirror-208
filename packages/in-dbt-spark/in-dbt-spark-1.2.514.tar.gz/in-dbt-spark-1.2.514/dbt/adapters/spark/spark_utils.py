from typing import Any

from jinja2.runtime import Undefined


def remove_undefined(v: Any) -> Any:
    return None if isinstance(v, Undefined) else v
