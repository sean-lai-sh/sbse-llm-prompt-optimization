from typing import List


def z_function(text: str, pattern: str) -> List[int]:
    if not pattern or not text:
        return []

    combined = pattern + "$" + text
    n = len(combined)
    z = [0] * n
    z[0] = n
    lo, hi = 0, 0

    for i in range(1, n):
        if i < hi:
            z[i] = min(hi - i, z[i - lo])
        while i + z[i] < n and combined[z[i]] == combined[i + z[i]]:
            z[i] += 1
        if i + z[i] > hi:
            lo, hi = i, i + z[i]

    m = len(pattern)
    results = []
    offset = m + 1
    for i in range(len(text)):
        if z[offset + i] == m:
            results.append(i)

    return results
