interface BIT {
  update: (index: number, delta: number) => void;
  prefixSum: (index: number) => number;
  rangeSum: (left: number, right: number) => number;
}

export function fenwickTree(nums: number[]): BIT {
  const n = nums.length;
  const tree: number[] = new Array(n + 1).fill(0);

  // Build BIT from initial array
  const buildUpdate = (i: number, delta: number): void => {
    i += 1; // 1-indexed
    while (i <= n) {
      tree[i] += delta;
      i += i & -i; // move to parent
    }
  };

  for (let i = 0; i < n; i++) {
    buildUpdate(i, nums[i]);
  }

  const update = (index: number, delta: number): void => {
    nums[index] += delta;
    let i = index + 1;
    while (i <= n) {
      tree[i] += delta;
      i += i & -i;
    }
  };

  const prefixSum = (index: number): number => {
    let sum = 0;
    let i = index + 1; // 1-indexed
    while (i > 0) {
      sum += tree[i];
      i -= i & -i; // move to parent
    }
    return sum;
  };

  const rangeSum = (left: number, right: number): number => {
    if (left === 0) return prefixSum(right);
    return prefixSum(right) - prefixSum(left - 1);
  };

  return { update, prefixSum, rangeSum };
}
