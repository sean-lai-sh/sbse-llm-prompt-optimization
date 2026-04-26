type Graph = Map<number, number[]>;

interface BFSResult {
  visited: number[];
  distances: Map<number, number>;
  parents: Map<number, number | null>;
}

export function graphBFS(graph: Graph, start: number): BFSResult {
  const visited: number[] = [];
  const distances = new Map<number, number>();
  const parents = new Map<number, number | null>();
  const queue: number[] = [start];
  const seen = new Set<number>([start]);

  distances.set(start, 0);
  parents.set(start, null);

  while (queue.length > 0) {
    const node = queue.shift()!;
    visited.push(node);

    const neighbors = graph.get(node) ?? [];
    for (const neighbor of neighbors) {
      if (!seen.has(neighbor)) {
        seen.add(neighbor);
        distances.set(neighbor, (distances.get(node) ?? 0) + 1);
        parents.set(neighbor, node);
        queue.push(neighbor);
      }
    }
  }

  return { visited, distances, parents };
}
