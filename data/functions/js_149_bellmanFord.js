export default function bellmanFord(n, edges, source) {
  const dist = new Array(n).fill(Infinity);
  const pred = new Array(n).fill(-1);
  dist[source] = 0;

  for (let i = 0; i < n - 1; i++) {
    let updated = false;
    for (const [u, v, w] of edges) {
      if (dist[u] !== Infinity && dist[u] + w < dist[v]) {
        dist[v] = dist[u] + w;
        pred[v] = u;
        updated = true;
      }
    }
    if (!updated) break;
  }

  const negCycles = [];
  for (const [u, v, w] of edges) {
    if (dist[u] !== Infinity && dist[u] + w < dist[v]) {
      negCycles.push([u, v]);
    }
  }

  function getPath(target) {
    if (dist[target] === Infinity) return null;
    const path = [];
    let cur = target;
    while (cur !== -1) {
      path.unshift(cur);
      cur = pred[cur];
    }
    return path[0] === source ? path : null;
  }

  return { dist, pred, negCycles, getPath };
}
