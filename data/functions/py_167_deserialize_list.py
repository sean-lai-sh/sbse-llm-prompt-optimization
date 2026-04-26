from typing import List


def deserialize_list(s: str) -> List[int]:
    if not s:
        return []
    return [int(x) for x in s.split(",")]
