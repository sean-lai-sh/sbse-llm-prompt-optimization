import heapq
from typing import Dict, List, Optional, Tuple


def dijkstra_shortest(
    graph: Dict[str, Dict[str, float]],
    start: str,
    end: Optional[str] = None
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    if start not in graph:
        raise ValueError(f"Start node '{start}' not in graph")

    dist: Dict[str, float] = {node: float('inf') for node in graph}
    dist[start] = 0.0
    prev: Dict[str, Optional[str]] = {node: None for node in graph}

    heap: List[Tuple[float, str]] = [(0.0, start)]
    visited = set()

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        if end is not None and current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            if weight < 0:
                raise ValueError(f"Negative weight found: {current_node} -> {neighbor}")
            if neighbor not in dist:
                dist[neighbor] = float('inf')
                prev[neighbor] = None
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return (dist, prev)
