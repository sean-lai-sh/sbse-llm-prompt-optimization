export function countingSort(arr: number[]): number[] {
  if (arr.length === 0) return [];
  const min = Math.min(...arr);
  const max = Math.max(...arr);
  const count = new Array<number>(max - min + 1).fill(0);
  for (const n of arr) count[n - min]++;
  const result: number[] = [];
  for (let i = 0; i < count.length; i++) {
    for (let j = 0; j < count[i]; j++) result.push(i + min);
  }
  return result;
}
