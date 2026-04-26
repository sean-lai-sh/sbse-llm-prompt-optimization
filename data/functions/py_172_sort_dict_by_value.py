from typing import Any, Dict, List, Tuple


def sort_dict_by_value(d: Dict[str, Any]) -> List[Tuple[str, Any]]:
    return sorted(d.items(), key=lambda kv: kv[1])
