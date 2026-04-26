export default function graphDFS(graph, start, options = {}) {
  // graph: adjacency list { node: [neighbors] }
  // options: { mode: 'traversal'|'topological'|'detectCycle'|'allPaths', target }

  const { mode = "traversal", target } = options;

  if (!(start in graph)) {
    if (mode === "allPaths") return [];
    if (mode === "detectCycle") return false;
    return [];
  }

  if (mode === "allPaths" && target !== undefined) {
    const allPaths = [];
    const dfsPath = (node, path, visited) => {
      if (node === target) { allPaths.push([...path]); return; }
      for (const neighbor of (graph[node] || [])) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          path.push(neighbor);
          dfsPath(neighbor, path, visited);
          path.pop();
          visited.delete(neighbor);
        }
      }
    };
    dfsPath(start, [start], new Set([start]));
    return allPaths;
  }

  if (mode === "detectCycle") {
    const visited = new Set();
    const recStack = new Set();
    const hasCycle = (node) => {
      visited.add(node);
      recStack.add(node);
      for (const neighbor of (graph[node] || [])) {
        if (!visited.has(neighbor)) {
          if (hasCycle(neighbor)) return true;
        } else if (recStack.has(neighbor)) {
          return true;
        }
      }
      recStack.delete(node);
      return false;
    };
    for (const node of Object.keys(graph)) {
      if (!visited.has(node) && hasCycle(node)) return true;
    }
    return false;
  }

  if (mode === "topological") {
    const visited = new Set();
    const stack = [];
    const dfsUtil = (node) => {
      visited.add(node);
      for (const neighbor of (graph[node] || [])) {
        if (!visited.has(neighbor)) dfsUtil(neighbor);
      }
      stack.push(node);
    };
    for (const node of Object.keys(graph)) {
      if (!visited.has(node)) dfsUtil(node);
    }
    return stack.reverse();
  }

  // Default: traversal (iterative DFS with discovery/finish times)
  const visited = new Set();
  const order = [];
  const discovery = {};
  const finish = {};
  let time = 0;

  const dfsRec = (node) => {
    visited.add(node);
    discovery[node] = ++time;
    order.push(node);
    for (const neighbor of (graph[node] || [])) {
      if (!visited.has(neighbor)) dfsRec(neighbor);
    }
    finish[node] = ++time;
  };

  dfsRec(start);
  for (const node of Object.keys(graph)) {
    if (!visited.has(node)) dfsRec(node);
  }
  return { order, discovery, finish };
}
