from typing import List


def fenwick_tree(nums: List[int], queries: List[tuple]) -> List[int]:
    n = len(nums)
    tree = [0] * (n + 1)

    def update(i: int, delta: int) -> None:
        i += 1
        while i <= n:
            tree[i] += delta
            i += i & (-i)

    def prefix_sum(i: int) -> int:
        i += 1
        total = 0
        while i > 0:
            total += tree[i]
            i -= i & (-i)
        return total

    def range_sum(lo: int, hi: int) -> int:
        if lo == 0:
            return prefix_sum(hi)
        return prefix_sum(hi) - prefix_sum(lo - 1)

    for idx, val in enumerate(nums):
        update(idx, val)

    results = []
    for q in queries:
        if q[0] == "sum":
            results.append(range_sum(q[1], q[2]))
        elif q[0] == "update":
            old_val = nums[q[1]]
            nums[q[1]] = q[2]
            update(q[1], q[2] - old_val)
        elif q[0] == "prefix":
            results.append(prefix_sum(q[1]))
    return results
