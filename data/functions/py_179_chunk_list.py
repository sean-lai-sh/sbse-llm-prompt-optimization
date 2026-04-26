from typing import Any, List


def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    return [lst[i:i + size] for i in range(0, len(lst), size)]
