interface FloydWarshallResult {
  distances: number[][];
  next: (number | null)[][];
  hasNegativeCycle: boolean;
}

export function floydWarshall(weights: number[][]): FloydWarshallResult {
  const n = weights.length;
  const INF = Infinity;

  // Initialize distance matrix
  const dist: number[][] = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (__, j) => {
      if (i === j) return 0;
      return weights[i][j] ?? INF;
    })
  );

  // Next-hop matrix for path reconstruction
  const next: (number | null)[][] = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (__, j) => {
      if (i === j) return null;
      return weights[i][j] !== undefined && weights[i][j] !== INF ? j : null;
    })
  );

  // Core Floyd-Warshall: relax through each intermediate vertex k
  for (let k = 0; k < n; k++) {
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (dist[i][k] !== INF && dist[k][j] !== INF) {
          if (dist[i][k] + dist[k][j] < dist[i][j]) {
            dist[i][j] = dist[i][k] + dist[k][j];
            next[i][j] = next[i][k];
          }
        }
      }
    }
  }

  // Check for negative cycles (any diagonal < 0)
  const hasNegativeCycle = dist.some((row, i) => row[i] < 0);

  return { distances: dist, next, hasNegativeCycle };
}
