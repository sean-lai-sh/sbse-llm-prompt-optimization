from typing import List


def find_all_permutations(s: str) -> List[str]:
    if len(s) <= 1:
        return [s]
    result = []
    for i, ch in enumerate(s):
        rest = s[:i] + s[i + 1:]
        for perm in find_all_permutations(rest):
            result.append(ch + perm)
    return result
