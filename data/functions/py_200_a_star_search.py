import heapq
from typing import Callable, Dict, List, Optional, Set, Tuple


def a_star_search(
    grid: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    heuristic: Optional[Callable[[Tuple[int, int], Tuple[int, int]], float]] = None,
) -> Optional[List[Tuple[int, int]]]:
    rows = len(grid)
    if rows == 0:
        return None
    cols = len(grid[0])

    if heuristic is None:
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = pos
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                result.append((nr, nc))
        return result

    g_score: Dict[Tuple[int, int], float] = {start: 0.0}
    f_score: Dict[Tuple[int, int], float] = {start: heuristic(start, goal)}
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    open_set: List[Tuple[float, Tuple[int, int]]] = [(f_score[start], start)]
    closed_set: Set[Tuple[int, int]] = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            node: Optional[Tuple[int, int]] = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor in neighbors(current):
            if neighbor in closed_set:
                continue
            tentative_g = g_score[current] + 1.0
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None
