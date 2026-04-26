export default function bellmanFord(n, edges, source) {
  // Bellman-Ford single-source shortest paths (handles negative weights)
  // edges: [[u, v, weight], ...] (directed)
  // Returns { dist, pred, hasNegativeCycle, negCycleNodes, getPath(target) }

  const dist = new Array(n).fill(Infinity);
  const pred = new Array(n).fill(-1);
  dist[source] = 0;

  // Relax all edges n-1 times
  for (let i = 0; i < n - 1; i++) {
    let updated = false;
    for (const [u, v, w] of edges) {
      if (dist[u] !== Infinity && dist[u] + w < dist[v]) {
        dist[v] = dist[u] + w;
        pred[v] = u;
        updated = true;
      }
    }
    if (!updated) break; // Early termination
  }

  // Detect negative cycles with an additional pass
  const inNegCycle = new Set();
  const negCycleEdges = [];
  for (const [u, v, w] of edges) {
    if (dist[u] !== Infinity && dist[u] + w < dist[v]) {
      inNegCycle.add(v);
      negCycleEdges.push([u, v, w]);
      // Propagate: nodes reachable from negative cycle also have -Infinity dist
      dist[v] = -Infinity;
    }
  }

  // Mark all nodes reachable from negative cycle as -Infinity
  const visited = new Set(inNegCycle);
  const queue = [...inNegCycle];
  while (queue.length > 0) {
    const node = queue.shift();
    for (const [u, v] of edges) {
      if (u === node && !visited.has(v)) {
        visited.add(v);
        dist[v] = -Infinity;
        queue.push(v);
      }
    }
  }

  const hasNegativeCycle = inNegCycle.size > 0;

  // Reconstruct path from source to target
  function getPath(target) {
    if (dist[target] === Infinity) return null; // unreachable
    if (dist[target] === -Infinity) return null; // in negative cycle
    const path = [];
    let cur = target;
    const seen = new Set();
    while (cur !== -1) {
      if (seen.has(cur)) return null; // cycle in pred chain
      seen.add(cur);
      path.unshift(cur);
      cur = pred[cur];
    }
    return path[0] === source ? path : null;
  }

  return {
    dist,
    pred,
    hasNegativeCycle,
    negCycleEdges,
    negCycleNodes: [...inNegCycle],
    getPath,
  };
}
