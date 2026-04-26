interface SegmentTree {
  update: (index: number, value: number) => void;
  query: (left: number, right: number) => number;
}

export function segmentTree(nums: number[]): SegmentTree {
  const n = nums.length;
  const tree: number[] = new Array(4 * n).fill(0);

  const build = (node: number, start: number, end: number): void => {
    if (start === end) {
      tree[node] = nums[start];
      return;
    }
    const mid = Math.floor((start + end) / 2);
    build(2 * node, start, mid);
    build(2 * node + 1, mid + 1, end);
    tree[node] = tree[2 * node] + tree[2 * node + 1];
  };

  const updateHelper = (node: number, start: number, end: number, index: number, value: number): void => {
    if (start === end) {
      tree[node] = value;
      nums[index] = value;
      return;
    }
    const mid = Math.floor((start + end) / 2);
    if (index <= mid) {
      updateHelper(2 * node, start, mid, index, value);
    } else {
      updateHelper(2 * node + 1, mid + 1, end, index, value);
    }
    tree[node] = tree[2 * node] + tree[2 * node + 1];
  };

  const queryHelper = (node: number, start: number, end: number, left: number, right: number): number => {
    if (right < start || end < left) return 0;
    if (left <= start && end <= right) return tree[node];
    const mid = Math.floor((start + end) / 2);
    return (
      queryHelper(2 * node, start, mid, left, right) +
      queryHelper(2 * node + 1, mid + 1, end, left, right)
    );
  };

  build(1, 0, n - 1);

  const update = (index: number, value: number): void => {
    updateHelper(1, 0, n - 1, index, value);
  };

  const query = (left: number, right: number): number => {
    return queryHelper(1, 0, n - 1, left, right);
  };

  return { update, query };
}
