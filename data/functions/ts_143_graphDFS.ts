type DFSGraph = Map<number, number[]>;

interface DFSResult {
  visited: number[];
  discoveryTime: Map<number, number>;
  finishTime: Map<number, number>;
  parents: Map<number, number | null>;
}

export function graphDFS(graph: DFSGraph, start: number): DFSResult {
  const visited: number[] = [];
  const discoveryTime = new Map<number, number>();
  const finishTime = new Map<number, number>();
  const parents = new Map<number, number | null>();
  const seen = new Set<number>();
  let timer = 0;

  const dfs = (node: number, parent: number | null): void => {
    seen.add(node);
    discoveryTime.set(node, timer++);
    parents.set(node, parent);
    visited.push(node);

    const neighbors = graph.get(node) ?? [];
    for (const neighbor of neighbors) {
      if (!seen.has(neighbor)) {
        dfs(neighbor, node);
      }
    }
    finishTime.set(node, timer++);
  };

  dfs(start, null);

  // Visit any remaining unvisited nodes (for disconnected graphs)
  for (const node of graph.keys()) {
    if (!seen.has(node)) {
      dfs(node, null);
    }
  }

  return { visited, discoveryTime, finishTime, parents };
}
