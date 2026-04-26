import json
from typing import Any, Optional, Union


def json_safe_parse(
    raw: Union[str, bytes],
    default: Optional[Any] = None,
    strict: bool = False,
    encoding: str = 'utf-8'
) -> Any:
    if raw is None:
        if strict:
            raise ValueError("Input cannot be None in strict mode")
        return default

    if isinstance(raw, bytes):
        try:
            raw = raw.decode(encoding)
        except (UnicodeDecodeError, LookupError) as exc:
            if strict:
                raise ValueError(f"Failed to decode bytes: {exc}") from exc
            return default

    if not isinstance(raw, str):
        if strict:
            raise TypeError(f"Expected str or bytes, got {type(raw).__name__}")
        return default

    raw = raw.strip()
    if not raw:
        if strict:
            raise ValueError("Input string is empty")
        return default

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        if strict:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        return default

    return parsed
