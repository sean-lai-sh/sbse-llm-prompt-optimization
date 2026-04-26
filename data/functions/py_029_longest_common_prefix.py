from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    if not strs:
        return ''
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ''
    return prefix
