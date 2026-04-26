interface Edge {
  from: number;
  to: number;
  weight: number;
}

interface BellmanFordResult {
  distances: number[];
  parents: (number | null)[];
  hasNegativeCycle: boolean;
  getPath: (target: number) => number[];
}

export function bellmanFord(
  vertices: number,
  edges: Edge[],
  source: number
): BellmanFordResult {
  const INF = Infinity;
  const distances: number[] = new Array(vertices).fill(INF);
  const parents: (number | null)[] = new Array(vertices).fill(null);

  distances[source] = 0;

  // Relax all edges (vertices - 1) times
  for (let i = 0; i < vertices - 1; i++) {
    let updated = false;
    for (const edge of edges) {
      if (distances[edge.from] !== INF && distances[edge.from] + edge.weight < distances[edge.to]) {
        distances[edge.to] = distances[edge.from] + edge.weight;
        parents[edge.to] = edge.from;
        updated = true;
      }
    }
    if (!updated) break; // Early termination if no update
  }

  // Check for negative cycles: if any edge can still be relaxed, there is a negative cycle
  let hasNegativeCycle = false;
  for (const edge of edges) {
    if (distances[edge.from] !== INF && distances[edge.from] + edge.weight < distances[edge.to]) {
      hasNegativeCycle = true;
      break;
    }
  }

  const getPath = (target: number): number[] => {
    if (distances[target] === INF) return [];
    const path: number[] = [];
    let current: number | null = target;
    const visited = new Set<number>();
    while (current !== null) {
      if (visited.has(current)) return []; // cycle detected
      visited.add(current);
      path.unshift(current);
      current = parents[current];
    }
    return path;
  };

  return { distances, parents, hasNegativeCycle, getPath };
}
