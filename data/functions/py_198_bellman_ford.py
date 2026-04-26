from typing import Dict, List, Optional, Tuple


def bellman_ford(
    num_nodes: int,
    edges: List[Tuple[int, int, int]],
    source: int,
) -> Optional[Dict[int, float]]:
    dist: Dict[int, float] = {i: float('inf') for i in range(num_nodes)}
    dist[source] = 0
    predecessor: Dict[int, Optional[int]] = {i: None for i in range(num_nodes)}

    for _ in range(num_nodes - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                predecessor[v] = u
                updated = True
            if dist[v] != float('inf') and dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                predecessor[u] = v
                updated = True
        if not updated:
            break

    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None
        if dist[v] != float('inf') and dist[v] + w < dist[u]:
            return None

    return dist
