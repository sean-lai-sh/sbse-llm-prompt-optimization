from typing import Dict, List, Optional, Set


def depth_first_search(graph: Dict[int, List[int]], start: int, target: int) -> Optional[List[int]]:
    visited: Set[int] = set()
    path: List[int] = []

    def dfs(node: int) -> bool:
        if node in visited:
            return False
        visited.add(node)
        path.append(node)
        if node == target:
            return True
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        path.pop()
        return False

    if dfs(start):
        return path
    return None
