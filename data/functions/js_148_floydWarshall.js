export default function floydWarshall(n, edges) {
  // All-pairs shortest paths using Floyd-Warshall algorithm
  // edges: [[u, v, weight], ...] (directed, may have negative weights)
  // Returns { dist, next, getPath(u,v), hasNegativeCycle }

  // Initialize distance matrix
  const dist = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 0 : Infinity))
  );

  // next[i][j] = next node on shortest path from i to j
  const next = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? i : null))
  );

  // Fill in direct edges
  for (const [u, v, w] of edges) {
    if (w < dist[u][v]) {
      dist[u][v] = w;
      next[u][v] = v;
    }
  }

  // Main DP loop
  for (let k = 0; k < n; k++) {
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (dist[i][k] !== Infinity && dist[k][j] !== Infinity) {
          const through = dist[i][k] + dist[k][j];
          if (through < dist[i][j]) {
            dist[i][j] = through;
            next[i][j] = next[i][k];
          }
        }
      }
    }
  }

  // Detect negative cycles (dist[i][i] < 0 after relaxation)
  let hasNegativeCycle = false;
  for (let i = 0; i < n; i++) {
    if (dist[i][i] < 0) { hasNegativeCycle = true; break; }
  }

  // Reconstruct shortest path from u to v
  function getPath(u, v) {
    if (dist[u][v] === Infinity) return null;
    if (next[u][v] === null) return null;
    const path = [u];
    let cur = u;
    let steps = 0;
    while (cur !== v) {
      cur = next[cur][v];
      path.push(cur);
      if (++steps > n) return null; // cycle detected
    }
    return path;
  }

  // Get transitive closure (which nodes are reachable from which)
  function getTransitiveClosure() {
    return Array.from({ length: n }, (_, i) =>
      Array.from({ length: n }, (_, j) => dist[i][j] !== Infinity)
    );
  }

  return { dist, next, getPath, hasNegativeCycle, getTransitiveClosure };
}
