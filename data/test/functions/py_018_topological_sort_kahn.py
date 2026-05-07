from collections import deque
from typing import Dict, List, Optional


def topological_sort_kahn(graph: Dict[int, List[int]]) -> Optional[List[int]]:
    """Kahn's algorithm. Returns a topological ordering of the DAG, or None if a cycle exists."""
    indeg: Dict[int, int] = {node: 0 for node in graph}
    for node, succs in graph.items():
        for s in succs:
            indeg[s] = indeg.get(s, 0) + 1
            indeg.setdefault(node, 0)
    queue: deque[int] = deque(sorted(n for n, d in indeg.items() if d == 0))
    order: List[int] = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for s in graph.get(n, []):
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    if len(order) != len(indeg):
        return None
    return order
