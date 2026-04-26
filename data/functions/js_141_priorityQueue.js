export default function priorityQueue(operations, comparator) {
  // Min-heap priority queue
  // operations: [{ type: 'push', value } | { type: 'pop' } | { type: 'peek' } | { type: 'size' }]
  // comparator: (a, b) => number, default is min-heap

  const cmp = comparator || ((a, b) => a - b);
  const heap = [];

  function swap(i, j) {
    [heap[i], heap[j]] = [heap[j], heap[i]];
  }

  function heapifyUp(i) {
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (cmp(heap[i], heap[parent]) < 0) {
        swap(i, parent);
        i = parent;
      } else break;
    }
  }

  function heapifyDown(i) {
    const n = heap.length;
    while (true) {
      let smallest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < n && cmp(heap[left], heap[smallest]) < 0) smallest = left;
      if (right < n && cmp(heap[right], heap[smallest]) < 0) smallest = right;
      if (smallest !== i) {
        swap(i, smallest);
        i = smallest;
      } else break;
    }
  }

  function push(val) {
    heap.push(val);
    heapifyUp(heap.length - 1);
  }

  function pop() {
    if (heap.length === 0) return undefined;
    const top = heap[0];
    const last = heap.pop();
    if (heap.length > 0) {
      heap[0] = last;
      heapifyDown(0);
    }
    return top;
  }

  function peek() {
    return heap.length > 0 ? heap[0] : undefined;
  }

  function buildFromArray(arr) {
    for (const v of arr) heap.push(v);
    for (let i = Math.floor(heap.length / 2) - 1; i >= 0; i--) {
      heapifyDown(i);
    }
  }

  const results = [];
  for (const op of operations) {
    if (op.type === "push") {
      push(op.value);
      results.push({ operation: "push", value: op.value });
    } else if (op.type === "pop") {
      results.push({ operation: "pop", value: pop() });
    } else if (op.type === "peek") {
      results.push({ operation: "peek", value: peek() });
    } else if (op.type === "size") {
      results.push({ operation: "size", size: heap.length });
    } else if (op.type === "build") {
      buildFromArray(op.values);
      results.push({ operation: "build", size: heap.length });
    }
  }
  return results;
}
