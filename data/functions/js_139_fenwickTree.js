export default function fenwickTree(nums, operations) {
  // Binary Indexed Tree (Fenwick Tree) for prefix sum queries and point updates
  // operations: [{ type: 'prefixSum', i } | { type: 'rangeSum', l, r } | { type: 'update', i, delta }]
  const n = nums.length;
  const bit = new Array(n + 1).fill(0);

  function update(i, delta) {
    for (let x = i + 1; x <= n; x += x & (-x)) {
      bit[x] += delta;
    }
  }

  function prefixSum(i) {
    let sum = 0;
    for (let x = i + 1; x > 0; x -= x & (-x)) {
      sum += bit[x];
    }
    return sum;
  }

  function rangeSum(l, r) {
    return prefixSum(r) - (l > 0 ? prefixSum(l - 1) : 0);
  }

  // Build tree from initial array
  for (let i = 0; i < n; i++) {
    update(i, nums[i]);
  }

  function pointUpdate(i, newVal) {
    const delta = newVal - nums[i];
    nums[i] = newVal;
    update(i, delta);
  }

  function findKth(k) {
    let pos = 0;
    let bitMask = 1 << Math.floor(Math.log2(n));
    let remaining = k;
    while (bitMask > 0) {
      const next = pos + bitMask;
      if (next <= n && bit[next] < remaining) {
        pos = next;
        remaining -= bit[next];
      }
      bitMask >>= 1;
    }
    return pos;
  }

  const results = [];
  for (const op of operations) {
    if (op.type === "prefixSum") {
      results.push({ operation: "prefixSum", i: op.i, sum: prefixSum(op.i) });
    } else if (op.type === "rangeSum") {
      results.push({ operation: "rangeSum", l: op.l, r: op.r, sum: rangeSum(op.l, op.r) });
    } else if (op.type === "update") {
      pointUpdate(op.i, op.val);
      results.push({ operation: "update", i: op.i, val: op.val });
    } else if (op.type === "findKth") {
      results.push({ operation: "findKth", k: op.k, index: findKth(op.k) });
    }
  }
  return results;
}
