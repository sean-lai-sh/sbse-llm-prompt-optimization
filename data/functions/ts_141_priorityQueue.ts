interface PriorityQueue<T> {
  push: (item: T) => void;
  pop: () => T | undefined;
  peek: () => T | undefined;
  size: () => number;
  isEmpty: () => boolean;
}

export function priorityQueue<T>(comparator: (a: T, b: T) => number): PriorityQueue<T> {
  const heap: T[] = [];

  const swap = (i: number, j: number): void => {
    [heap[i], heap[j]] = [heap[j], heap[i]];
  };

  const parentIdx = (i: number): number => Math.floor((i - 1) / 2);
  const leftIdx = (i: number): number => 2 * i + 1;
  const rightIdx = (i: number): number => 2 * i + 2;

  const bubbleUp = (i: number): void => {
    while (i > 0) {
      const parent = parentIdx(i);
      if (comparator(heap[i], heap[parent]) < 0) {
        swap(i, parent);
        i = parent;
      } else {
        break;
      }
    }
  };

  const bubbleDown = (i: number): void => {
    const n = heap.length;
    while (true) {
      let smallest = i;
      const left = leftIdx(i);
      const right = rightIdx(i);
      if (left < n && comparator(heap[left], heap[smallest]) < 0) smallest = left;
      if (right < n && comparator(heap[right], heap[smallest]) < 0) smallest = right;
      if (smallest === i) break;
      swap(i, smallest);
      i = smallest;
    }
  };

  const push = (item: T): void => {
    heap.push(item);
    bubbleUp(heap.length - 1);
  };

  const pop = (): T | undefined => {
    if (heap.length === 0) return undefined;
    const top = heap[0];
    const last = heap.pop()!;
    if (heap.length > 0) {
      heap[0] = last;
      bubbleDown(0);
    }
    return top;
  };

  const peek = (): T | undefined => heap[0];
  const size = (): number => heap.length;
  const isEmpty = (): boolean => heap.length === 0;

  return { push, pop, peek, size, isEmpty };
}
