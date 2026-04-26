export default function aStarSearch(grid, start, goal) {
  const rows = grid.length;
  const cols = grid[0].length;
  const h = (r, c) => Math.abs(r - goal[0]) + Math.abs(c - goal[1]);

  const gScore = Array.from({ length: rows }, () => new Array(cols).fill(Infinity));
  const fScore = Array.from({ length: rows }, () => new Array(cols).fill(Infinity));
  const cameFrom = {};

  gScore[start[0]][start[1]] = 0;
  fScore[start[0]][start[1]] = h(start[0], start[1]);

  const open = [start];
  const inOpen = new Set([`${start[0]},${start[1]}`]);

  while (open.length > 0) {
    open.sort((a, b) => fScore[a[0]][a[1]] - fScore[b[0]][b[1]]);
    const [r, c] = open.shift();
    inOpen.delete(`${r},${c}`);

    if (r === goal[0] && c === goal[1]) {
      const path = [];
      let cur = `${r},${c}`;
      while (cur) {
        const [pr, pc] = cur.split(',').map(Number);
        path.unshift([pr, pc]);
        cur = cameFrom[cur];
      }
      return path;
    }

    for (const [dr, dc] of [[-1,0],[1,0],[0,-1],[0,1]]) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols || grid[nr][nc] === 1) continue;
      const tentativeG = gScore[r][c] + 1;
      if (tentativeG < gScore[nr][nc]) {
        cameFrom[`${nr},${nc}`] = `${r},${c}`;
        gScore[nr][nc] = tentativeG;
        fScore[nr][nc] = tentativeG + h(nr, nc);
        if (!inOpen.has(`${nr},${nc}`)) {
          open.push([nr, nc]);
          inOpen.add(`${nr},${nc}`);
        }
      }
    }
  }
  return null;
}
