from typing import List, Tuple


def union_find_with_rank(n: int, edges: List[Tuple[int, int]]) -> List[List[int]]:
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> bool:
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    components: dict = {}
    for edge in edges:
        union(edge[0], edge[1])

    for i in range(n):
        root = find(i)
        if root not in components:
            components[root] = []
        components[root].append(i)

    return sorted([sorted(comp) for comp in components.values()])
