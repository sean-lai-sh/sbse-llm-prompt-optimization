from typing import Dict, List, Optional, Set


def topological_sort(
    graph: Dict[str, List[str]],
    detect_cycle: bool = True
) -> Optional[List[str]]:
    if not graph:
        return []

    all_nodes: Set[str] = set(graph.keys())
    for neighbors in graph.values():
        all_nodes.update(neighbors)

    visited: Set[str] = set()
    in_stack: Set[str] = set()
    result: List[str] = []
    has_cycle = False

    def dfs(node: str) -> None:
        nonlocal has_cycle
        if has_cycle:
            return
        if node in in_stack:
            has_cycle = True
            return
        if node in visited:
            return
        in_stack.add(node)
        visited.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        in_stack.discard(node)
        result.append(node)

    for node in sorted(all_nodes):
        if node not in visited:
            dfs(node)
            if has_cycle:
                if detect_cycle:
                    return None
                break

    return list(reversed(result))
