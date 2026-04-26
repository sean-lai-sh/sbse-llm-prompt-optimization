export default function aStarSearch(grid, start, goal, options = {}) {
  // A* pathfinding on a 2D grid
  // grid: 2D array where 0 = passable, 1 = wall
  // start, goal: [row, col]
  // options: { diagonal: bool, heuristic: 'manhattan'|'euclidean'|'chebyshev' }

  const rows = grid.length;
  const cols = grid[0].length;
  const { diagonal = false, heuristic = "manhattan" } = options;

  const h = (r, c) => {
    const dr = Math.abs(r - goal[0]);
    const dc = Math.abs(c - goal[1]);
    if (heuristic === "euclidean") return Math.sqrt(dr * dr + dc * dc);
    if (heuristic === "chebyshev") return Math.max(dr, dc);
    return dr + dc; // manhattan
  };

  const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]];
  if (diagonal) dirs.push([-1, -1], [-1, 1], [1, -1], [1, 1]);

  const gScore = Array.from({ length: rows }, () => new Array(cols).fill(Infinity));
  const fScore = Array.from({ length: rows }, () => new Array(cols).fill(Infinity));
  const cameFrom = {};
  const closed = new Set();

  gScore[start[0]][start[1]] = 0;
  fScore[start[0]][start[1]] = h(start[0], start[1]);

  const open = [[...start]];
  const inOpen = new Set([`${start[0]},${start[1]}`]);

  while (open.length > 0) {
    // Get node with lowest fScore
    open.sort((a, b) => fScore[a[0]][a[1]] - fScore[b[0]][b[1]]);
    const [r, c] = open.shift();
    const key = `${r},${c}`;
    inOpen.delete(key);
    closed.add(key);

    if (r === goal[0] && c === goal[1]) {
      // Reconstruct path
      const path = [];
      let cur = key;
      while (cur) {
        const [pr, pc] = cur.split(",").map(Number);
        path.unshift([pr, pc]);
        cur = cameFrom[cur];
      }
      return { path, cost: gScore[goal[0]][goal[1]], explored: closed.size };
    }

    for (const [dr, dc] of dirs) {
      const nr = r + dr;
      const nc = c + dc;
      const nKey = `${nr},${nc}`;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
      if (grid[nr][nc] === 1) continue;
      if (closed.has(nKey)) continue;

      const moveCost = Math.abs(dr) + Math.abs(dc) > 1 ? Math.SQRT2 : 1;
      const tentativeG = gScore[r][c] + moveCost;
      if (tentativeG < gScore[nr][nc]) {
        cameFrom[nKey] = key;
        gScore[nr][nc] = tentativeG;
        fScore[nr][nc] = tentativeG + h(nr, nc);
        if (!inOpen.has(nKey)) {
          open.push([nr, nc]);
          inOpen.add(nKey);
        }
      }
    }
  }

  return { path: null, cost: Infinity, explored: closed.size };
}
