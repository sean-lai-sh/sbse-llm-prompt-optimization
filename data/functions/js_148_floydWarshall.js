export default function floydWarshall(n, edges) {
  const dist = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 0 : Infinity))
  );
  const next = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? i : null))
  );

  for (const [u, v, w] of edges) {
    if (w < dist[u][v]) {
      dist[u][v] = w;
      next[u][v] = v;
    }
  }

  for (let k = 0; k < n; k++) {
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (dist[i][k] !== Infinity && dist[k][j] !== Infinity) {
          if (dist[i][k] + dist[k][j] < dist[i][j]) {
            dist[i][j] = dist[i][k] + dist[k][j];
            next[i][j] = next[i][k];
          }
        }
      }
    }
  }

  function getPath(u, v) {
    if (next[u][v] === null) return [];
    const path = [u];
    while (u !== v) {
      u = next[u][v];
      path.push(u);
    }
    return path;
  }

  return { dist, getPath };
}
