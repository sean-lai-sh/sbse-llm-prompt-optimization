from typing import Dict, List


def boyer_moore_search(text: str, pattern: str) -> List[int]:
    if not pattern or not text:
        return []

    m, n = len(pattern), len(text)
    if m > n:
        return []

    bad_char: Dict[str, int] = {}
    for i, ch in enumerate(pattern):
        bad_char[ch] = i

    good_suffix = [0] * (m + 1)
    border = [0] * (m + 1)
    i = m
    j = m + 1
    border[i] = j
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if good_suffix[j] == 0:
                good_suffix[j] = j - i
            j = border[j]
        i -= 1
        j -= 1
        border[i] = j

    j = border[0]
    for k in range(m + 1):
        if good_suffix[k] == 0:
            good_suffix[k] = j
        if k == j:
            j = border[j]

    results = []
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            results.append(i)
            i += good_suffix[0]
        else:
            bc_shift = j - bad_char.get(text[i + j], -1)
            gs_shift = good_suffix[j + 1]
            i += max(bc_shift, gs_shift)

    return results
