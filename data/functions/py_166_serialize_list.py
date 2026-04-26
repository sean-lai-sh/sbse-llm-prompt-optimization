from typing import List


def serialize_list(lst: List[int]) -> str:
    return ",".join(str(x) for x in lst)
