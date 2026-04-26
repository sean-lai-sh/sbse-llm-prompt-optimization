from typing import List, Tuple


def decode_run_length(encoded: List[Tuple[str, int]]) -> str:
    result = []
    for ch, count in encoded:
        result.append(ch * count)
    return "".join(result)
