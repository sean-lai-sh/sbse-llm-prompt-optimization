export default function graphBFS(graph, start, options = {}) {
  // graph: adjacency list { node: [neighbors] }
  // options: { target, mode: 'traversal'|'shortestPath'|'levelOrder' }
  // Returns traversal order or shortest path to target

  const { target, mode = "traversal" } = options;

  if (!(start in graph)) return mode === "traversal" ? [] : null;

  const visited = new Set();
  const queue = [start];
  visited.add(start);

  if (mode === "shortestPath" && target !== undefined) {
    const parent = { [start]: null };
    while (queue.length > 0) {
      const node = queue.shift();
      if (node === target) {
        const path = [];
        let cur = target;
        while (cur !== null) {
          path.unshift(cur);
          cur = parent[cur];
        }
        return path;
      }
      for (const neighbor of (graph[node] || [])) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          parent[neighbor] = node;
          queue.push(neighbor);
        }
      }
    }
    return null;
  }

  if (mode === "levelOrder") {
    const levels = [];
    let currentLevel = [start];
    while (currentLevel.length > 0) {
      levels.push([...currentLevel]);
      const nextLevel = [];
      for (const node of currentLevel) {
        for (const neighbor of (graph[node] || [])) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            nextLevel.push(neighbor);
          }
        }
      }
      currentLevel = nextLevel;
    }
    return levels;
  }

  // Default: traversal order
  const order = [];
  const bfsQueue = [start];
  const seen = new Set([start]);
  while (bfsQueue.length > 0) {
    const node = bfsQueue.shift();
    order.push(node);
    for (const neighbor of (graph[node] || [])) {
      if (!seen.has(neighbor)) {
        seen.add(neighbor);
        bfsQueue.push(neighbor);
      }
    }
  }
  return order;
}
