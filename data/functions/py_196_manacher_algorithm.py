from typing import List


def manacher_algorithm(s: str) -> List[int]:
    if not s:
        return []

    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    center = right = 0

    for i in range(n):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])
        while (i + p[i] + 1 < n and
               i - p[i] - 1 >= 0 and
               t[i + p[i] + 1] == t[i - p[i] - 1]):
            p[i] += 1
        if i + p[i] > right:
            center = i
            right = i + p[i]

    radii = []
    for i in range(n):
        if t[i] != '#':
            orig_idx = i // 2
            radius = p[i] // 2
            radii.append(radius)

    best_start = 0
    best_len = 1
    for i in range(n):
        if t[i] == '#':
            continue
        orig_i = i // 2
        radius = p[i] // 2
        length = 2 * radius + 1
        if length > best_len:
            best_len = length
            best_start = orig_i - radius

    result = [0] * len(s)
    for i in range(n):
        if t[i] == '#':
            continue
        orig_i = i // 2
        result[orig_i] = p[i] // 2

    return result
