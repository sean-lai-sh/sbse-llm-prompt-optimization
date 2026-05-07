export function partitionByPivot(arr: number[], pivot: number): number[] {
  const less: number[] = [];
  const equal: number[] = [];
  const greater: number[] = [];
  for (const n of arr) {
    if (n < pivot) less.push(n);
    else if (n === pivot) equal.push(n);
    else greater.push(n);
  }
  return [...less, ...equal, ...greater];
}
