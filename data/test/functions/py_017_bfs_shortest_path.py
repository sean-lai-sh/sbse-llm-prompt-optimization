from collections import deque
from typing import Dict, List, Optional


def bfs_shortest_path(graph: Dict[int, List[int]], src: int, dst: int) -> Optional[List[int]]:
    """Return the shortest path (by edge count) from src to dst in an unweighted graph.

    Returns None if dst is unreachable. The path includes both endpoints.
    """
    if src == dst:
        return [src]
    if src not in graph:
        return None
    visited = {src}
    parent: Dict[int, int] = {}
    queue: deque[int] = deque([src])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = node
            if nxt == dst:
                path = [dst]
                cur = dst
                while cur in parent:
                    cur = parent[cur]
                    path.append(cur)
                return list(reversed(path))
            queue.append(nxt)
    return None
