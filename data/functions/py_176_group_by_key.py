from typing import Any, Dict, List


def group_by_key(records: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    groups: Dict[Any, List[Dict[str, Any]]] = {}
    for record in records:
        val = record.get(key)
        if val not in groups:
            groups[val] = []
        groups[val].append(record)
    return groups
