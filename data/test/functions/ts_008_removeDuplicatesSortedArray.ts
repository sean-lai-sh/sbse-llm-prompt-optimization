export function removeDuplicatesSortedArray(arr: number[]): number {
  if (arr.length === 0) return 0;
  let write = 1;
  for (let read = 1; read < arr.length; read += 1) {
    if (arr[read] !== arr[write - 1]) {
      arr[write] = arr[read];
      write += 1;
    }
  }
  arr.length = write;
  return write;
}
