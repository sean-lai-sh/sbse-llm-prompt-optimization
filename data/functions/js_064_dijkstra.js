export default function dijkstra(graph, source) {
  // graph: { node: [[neighbor, weight], ...] }
  const dist = {};
  const prev = {};
  const visited = new Set();

  // Initialize distances
  for (const node of Object.keys(graph)) {
    dist[node] = Infinity;
    prev[node] = null;
  }
  dist[source] = 0;

  // Simple priority queue using a sorted array
  const queue = [{ node: source, dist: 0 }];

  while (queue.length > 0) {
    // Extract node with minimum distance
    queue.sort((a, b) => a.dist - b.dist);
    const { node: u } = queue.shift();

    if (visited.has(u)) continue;
    visited.add(u);

    if (!graph[u]) continue;

    for (const [v, weight] of graph[u]) {
      if (visited.has(v)) continue;
      const alt = dist[u] + weight;
      if (alt < dist[v]) {
        dist[v] = alt;
        prev[v] = u;
        queue.push({ node: v, dist: alt });
      }
    }
  }

  // Build path helper
  function getPath(target) {
    const path = [];
    let current = target;
    while (current !== null) {
      path.unshift(current);
      current = prev[current];
    }
    return dist[target] === Infinity ? [] : path;
  }

  return { dist, prev, getPath };
}
