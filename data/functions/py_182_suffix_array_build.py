from typing import List


def suffix_array_build(s: str) -> List[int]:
    n = len(s)
    if n == 0:
        return []
    sa = list(range(n))
    rank = [ord(c) for c in s]
    tmp = [0] * n
    k = 1
    while k < n:
        def sort_key(i: int) -> tuple:
            return (rank[i], rank[i + k] if i + k < n else -1)

        sa.sort(key=sort_key)
        tmp[sa[0]] = 0
        for j in range(1, n):
            prev, cur = sa[j - 1], sa[j]
            if sort_key(prev) == sort_key(cur):
                tmp[cur] = tmp[prev]
            else:
                tmp[cur] = tmp[prev] + 1
        rank = tmp[:]
        if rank[sa[-1]] == n - 1:
            break
        k *= 2
    return sa


