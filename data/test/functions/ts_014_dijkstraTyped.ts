type Edge = { to: number; weight: number };

export function dijkstraTyped(graph: Map<number, Edge[]>, source: number): Map<number, number> {
  const dist = new Map<number, number>();
  for (const node of graph.keys()) dist.set(node, Number.POSITIVE_INFINITY);
  dist.set(source, 0);

  const visited = new Set<number>();
  const pending = new Set<number>(graph.keys());
  while (pending.size > 0) {
    let current: number | null = null;
    let currentDist = Number.POSITIVE_INFINITY;
    for (const node of pending) {
      const d = dist.get(node) ?? Number.POSITIVE_INFINITY;
      if (d < currentDist) {
        currentDist = d;
        current = node;
      }
    }
    if (current === null || currentDist === Number.POSITIVE_INFINITY) break;
    pending.delete(current);
    visited.add(current);
    for (const edge of graph.get(current) ?? []) {
      if (visited.has(edge.to)) continue;
      const alt = currentDist + edge.weight;
      if (alt < (dist.get(edge.to) ?? Number.POSITIVE_INFINITY)) {
        dist.set(edge.to, alt);
      }
    }
  }
  return dist;
}
