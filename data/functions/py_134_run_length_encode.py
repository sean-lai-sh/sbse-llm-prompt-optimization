from typing import List, Tuple


def run_length_encode(s: str) -> List[Tuple[str, int]]:
    if not s:
        return []
    result = []
    current = s[0]
    count = 1
    for ch in s[1:]:
        if ch == current:
            count += 1
        else:
            result.append((current, count))
            current = ch
            count = 1
    result.append((current, count))
    return result
