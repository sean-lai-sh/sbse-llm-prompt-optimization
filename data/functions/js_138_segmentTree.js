export default function segmentTree(nums, operations) {
  // Segment tree for range sum queries and point updates
  // operations: [{ type: 'query', l, r } | { type: 'update', i, val }]
  const n = nums.length;
  const tree = new Array(4 * n).fill(0);

  function build(node, start, end) {
    if (start === end) {
      tree[node] = nums[start];
      return;
    }
    const mid = Math.floor((start + end) / 2);
    build(2 * node, start, mid);
    build(2 * node + 1, mid + 1, end);
    tree[node] = tree[2 * node] + tree[2 * node + 1];
  }

  function update(node, start, end, idx, val) {
    if (start === end) {
      nums[idx] = val;
      tree[node] = val;
      return;
    }
    const mid = Math.floor((start + end) / 2);
    if (idx <= mid) {
      update(2 * node, start, mid, idx, val);
    } else {
      update(2 * node + 1, mid + 1, end, idx, val);
    }
    tree[node] = tree[2 * node] + tree[2 * node + 1];
  }

  function query(node, start, end, l, r) {
    if (r < start || end < l) return 0;
    if (l <= start && end <= r) return tree[node];
    const mid = Math.floor((start + end) / 2);
    return (
      query(2 * node, start, mid, l, r) +
      query(2 * node + 1, mid + 1, end, l, r)
    );
  }

  function rangeMin(node, start, end, l, r) {
    if (r < start || end < l) return Infinity;
    if (l <= start && end <= r) return tree[node];
    const mid = Math.floor((start + end) / 2);
    return Math.min(
      rangeMin(2 * node, start, mid, l, r),
      rangeMin(2 * node + 1, mid + 1, end, l, r)
    );
  }

  build(1, 0, n - 1);

  const results = [];
  for (const op of operations) {
    if (op.type === "query") {
      results.push({ operation: "query", l: op.l, r: op.r, sum: query(1, 0, n - 1, op.l, op.r) });
    } else if (op.type === "update") {
      update(1, 0, n - 1, op.i, op.val);
      results.push({ operation: "update", i: op.i, val: op.val });
    }
  }
  return results;
}
