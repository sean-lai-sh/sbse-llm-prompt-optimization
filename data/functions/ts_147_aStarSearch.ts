interface GridPoint {
  row: number;
  col: number;
}

interface AStarResult {
  path: GridPoint[];
  found: boolean;
  cost: number;
}

interface AStarNode {
  point: GridPoint;
  g: number; // cost from start
  h: number; // heuristic to end
  f: number; // g + h
  parent: AStarNode | null;
}

export function aStarSearch(
  grid: number[][],
  start: GridPoint,
  end: GridPoint
): AStarResult {
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;

  const heuristic = (a: GridPoint, b: GridPoint): number =>
    Math.abs(a.row - b.row) + Math.abs(a.col - b.col);

  const key = (p: GridPoint): string => `${p.row},${p.col}`;

  const openSet: AStarNode[] = [];
  const closedSet = new Set<string>();
  const gScore = new Map<string, number>();

  const startNode: AStarNode = {
    point: start,
    g: 0,
    h: heuristic(start, end),
    f: heuristic(start, end),
    parent: null,
  };

  openSet.push(startNode);
  gScore.set(key(start), 0);

  const directions: GridPoint[] = [
    { row: -1, col: 0 }, { row: 1, col: 0 },
    { row: 0, col: -1 }, { row: 0, col: 1 },
  ];

  while (openSet.length > 0) {
    // Find node with lowest f
    openSet.sort((a, b) => a.f - b.f);
    const current = openSet.shift()!;
    const currentKey = key(current.point);

    if (current.point.row === end.row && current.point.col === end.col) {
      // Reconstruct path
      const path: GridPoint[] = [];
      let node: AStarNode | null = current;
      while (node) {
        path.unshift(node.point);
        node = node.parent;
      }
      return { path, found: true, cost: current.g };
    }

    closedSet.add(currentKey);

    for (const dir of directions) {
      const neighbor: GridPoint = {
        row: current.point.row + dir.row,
        col: current.point.col + dir.col,
      };
      const nKey = key(neighbor);

      if (
        neighbor.row < 0 || neighbor.row >= rows ||
        neighbor.col < 0 || neighbor.col >= cols ||
        grid[neighbor.row][neighbor.col] === 1 ||
        closedSet.has(nKey)
      ) continue;

      const tentativeG = current.g + 1;
      if (tentativeG < (gScore.get(nKey) ?? Infinity)) {
        gScore.set(nKey, tentativeG);
        const h = heuristic(neighbor, end);
        const neighborNode: AStarNode = {
          point: neighbor,
          g: tentativeG,
          h,
          f: tentativeG + h,
          parent: current,
        };
        openSet.push(neighborNode);
      }
    }
  }

  return { path: [], found: false, cost: Infinity };
}
