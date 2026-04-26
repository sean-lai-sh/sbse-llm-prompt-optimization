from collections import deque
from typing import Dict, List, Optional, Tuple


def ford_fulkerson_max_flow(
    num_nodes: int,
    edges: List[Tuple[int, int, int]],
    source: int,
    sink: int,
) -> int:
    capacity: Dict[Tuple[int, int], int] = {}
    graph: Dict[int, List[int]] = {i: [] for i in range(num_nodes)}

    for u, v, cap in edges:
        capacity[(u, v)] = capacity.get((u, v), 0) + cap
        if v not in graph[u]:
            graph[u].append(v)
        if u not in graph[v]:
            graph[v].append(u)

    def bfs(parent: Dict[int, Optional[int]]) -> bool:
        visited = {source}
        queue: deque = deque([source])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in visited and capacity.get((u, v), 0) > 0:
                    visited.add(v)
                    parent[v] = u
                    if v == sink:
                        return True
                    queue.append(v)
        return False

    max_flow = 0
    while True:
        parent: Dict[int, Optional[int]] = {source: None}
        if not bfs(parent):
            break
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            assert u is not None
            path_flow = min(path_flow, capacity.get((u, v), 0))
            v = u
        v = sink
        while v != source:
            u = parent[v]
            assert u is not None
            capacity[(u, v)] = capacity.get((u, v), 0) - path_flow
            capacity[(v, u)] = capacity.get((v, u), 0) + path_flow
            v = u
        max_flow += int(path_flow)

    return max_flow
