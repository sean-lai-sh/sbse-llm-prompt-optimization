from typing import Any, Dict


def invert_dict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    inverted: Dict[Any, Any] = {}
    for key, value in d.items():
        if value in inverted:
            if isinstance(inverted[value], list):
                inverted[value].append(key)
            else:
                inverted[value] = [inverted[value], key]
        else:
            inverted[value] = key
    return inverted
