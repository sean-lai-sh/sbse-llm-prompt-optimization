from typing import List


def segment_tree_range_sum(nums: List[int], queries: List[tuple]) -> List[int]:
    n = len(nums)
    if n == 0:
        return []
    tree = [0] * (4 * n)

    def build(node: int, start: int, end: int) -> None:
        if start == end:
            tree[node] = nums[start]
            return
        mid = (start + end) // 2
        build(2 * node, start, mid)
        build(2 * node + 1, mid + 1, end)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

    def update(node: int, start: int, end: int, idx: int, val: int) -> None:
        if start == end:
            tree[node] = val
            nums[idx] = val
            return
        mid = (start + end) // 2
        if idx <= mid:
            update(2 * node, start, mid, idx, val)
        else:
            update(2 * node + 1, mid + 1, end, idx, val)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

    def query(node: int, start: int, end: int, lo: int, hi: int) -> int:
        if hi < start or end < lo:
            return 0
        if lo <= start and end <= hi:
            return tree[node]
        mid = (start + end) // 2
        return (query(2 * node, start, mid, lo, hi) +
                query(2 * node + 1, mid + 1, end, lo, hi))

    build(1, 0, n - 1)
    results = []
    for q in queries:
        if q[0] == "sum":
            results.append(query(1, 0, n - 1, q[1], q[2]))
        elif q[0] == "update":
            update(1, 0, n - 1, q[1], q[2])
    return results
