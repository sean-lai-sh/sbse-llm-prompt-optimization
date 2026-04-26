from typing import Any, Dict


def deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = deep_copy_dict(value)
        elif isinstance(value, list):
            result[key] = [
                deep_copy_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
