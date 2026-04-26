export default function unionFind(n, operations) {
  // n: number of elements (0..n-1)
  // operations: [{ type: 'union'|'find'|'connected', x, y }]
  // Returns array of results for 'find' and 'connected' ops

  const parent = Array.from({ length: n }, (_, i) => i);
  const rank = new Array(n).fill(0);
  const size = new Array(n).fill(1);

  function find(x) {
    if (parent[x] !== x) parent[x] = find(parent[x]); // path compression
    return parent[x];
  }

  function union(x, y) {
    const rx = find(x);
    const ry = find(y);
    if (rx === ry) return false;
    // Union by rank
    if (rank[rx] < rank[ry]) {
      parent[rx] = ry;
      size[ry] += size[rx];
    } else if (rank[rx] > rank[ry]) {
      parent[ry] = rx;
      size[rx] += size[ry];
    } else {
      parent[ry] = rx;
      size[rx] += size[ry];
      rank[rx]++;
    }
    return true;
  }

  function connected(x, y) {
    return find(x) === find(y);
  }

  function componentSize(x) {
    return size[find(x)];
  }

  function countComponents() {
    const roots = new Set();
    for (let i = 0; i < n; i++) roots.add(find(i));
    return roots.size;
  }

  const results = [];
  for (const op of operations) {
    if (op.type === "union") {
      results.push({ operation: "union", x: op.x, y: op.y, merged: union(op.x, op.y) });
    } else if (op.type === "find") {
      results.push({ operation: "find", x: op.x, root: find(op.x) });
    } else if (op.type === "connected") {
      results.push({ operation: "connected", x: op.x, y: op.y, result: connected(op.x, op.y) });
    } else if (op.type === "componentSize") {
      results.push({ operation: "componentSize", x: op.x, size: componentSize(op.x) });
    } else if (op.type === "countComponents") {
      results.push({ operation: "countComponents", count: countComponents() });
    }
  }
  return results;
}
