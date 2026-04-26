export default function topologicalSort(graph) {
  // graph: { node: [neighbors] } — directed acyclic graph
  const visited = new Set();
  const stack = [];
  const inStack = new Set(); // for cycle detection

  function dfs(node) {
    if (inStack.has(node)) {
      throw new Error(`Cycle detected at node: ${node}`);
    }
    if (visited.has(node)) return;

    inStack.add(node);
    visited.add(node);

    const neighbors = graph[node] || [];
    for (const neighbor of neighbors) {
      dfs(neighbor);
    }

    inStack.delete(node);
    stack.unshift(node);
  }

  // Visit all nodes (handles disconnected graphs)
  for (const node of Object.keys(graph)) {
    if (!visited.has(node)) {
      dfs(node);
    }
  }

  // Ensure all neighbor nodes are included even if not listed as keys
  const allNodes = new Set([
    ...Object.keys(graph),
    ...Object.values(graph).flat(),
  ]);
  for (const node of allNodes) {
    if (!visited.has(node)) {
      stack.push(node);
    }
  }

  return stack;
}
