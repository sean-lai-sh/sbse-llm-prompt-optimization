export interface Edge {
  to: number;
  weight: number;
}

export interface DijkstraResult {
  distances: number[];
  previous: (number | null)[];
}

/**
 * Dijkstra's shortest-path algorithm on a weighted directed graph.
 * `graph[u]` is an array of edges from node u.
 * Returns shortest distances from `source` to every other node, and
 * the predecessor array for path reconstruction.
 */
export function dijkstra(
  graph: Edge[][],
  source: number
): DijkstraResult {
  const n = graph.length;
  const INF = Infinity;
  const dist = new Array<number>(n).fill(INF);
  const prev: (number | null)[] = new Array(n).fill(null);
  const visited = new Array<boolean>(n).fill(false);

  dist[source] = 0;

  // Min-heap simulation using a simple priority queue array
  // Each entry: [distance, node]
  const pq: [number, number][] = [[0, source]];

  while (pq.length > 0) {
    // Extract min
    pq.sort((a, b) => a[0] - b[0]);
    const [d, u] = pq.shift()!;

    if (visited[u]) continue;
    visited[u] = true;

    for (const { to: v, weight: w } of graph[u]) {
      if (visited[v]) continue;
      const newDist = d + w;
      if (newDist < dist[v]) {
        dist[v] = newDist;
        prev[v] = u;
        pq.push([newDist, v]);
      }
    }
  }

  return { distances: dist, previous: prev };
}
