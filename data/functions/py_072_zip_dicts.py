from typing import Any, Dict, List


def zip_dicts(keys: List[Any], values: List[Any]) -> Dict[Any, Any]:
    if len(keys) != len(values):
        raise ValueError("keys and values must have the same length")
    return dict(zip(keys, values))
