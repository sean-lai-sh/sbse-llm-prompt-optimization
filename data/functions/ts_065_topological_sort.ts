export interface TopoSortResult {
  order: number[];
  hasCycle: boolean;
}

/**
 * Topological sort of a directed graph using Kahn's algorithm (BFS).
 * `graph[u]` lists nodes that u has edges to.
 * Returns the topological ordering, or hasCycle=true if a cycle is detected.
 */
export function topologicalSort(graph: number[][]): TopoSortResult {
  const n = graph.length;
  const inDegree = new Array<number>(n).fill(0);

  for (let u = 0; u < n; u++) {
    for (const v of graph[u]) {
      inDegree[v]++;
    }
  }

  const queue: number[] = [];
  for (let i = 0; i < n; i++) {
    if (inDegree[i] === 0) queue.push(i);
  }

  const order: number[] = [];
  let processed = 0;

  while (queue.length > 0) {
    const u = queue.shift()!;
    order.push(u);
    processed++;

    for (const v of graph[u]) {
      inDegree[v]--;
      if (inDegree[v] === 0) queue.push(v);
    }
  }

  if (processed !== n) {
    return { order: [], hasCycle: true };
  }

  return { order, hasCycle: false };
}
