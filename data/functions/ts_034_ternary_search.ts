export function ternarySearch(arr: number[], target: number): number {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const third = Math.floor((hi - lo) / 3);
    const mid1 = lo + third;
    const mid2 = hi - third;
    if (arr[mid1] === target) return mid1;
    if (arr[mid2] === target) return mid2;
    if (target < arr[mid1]) hi = mid1 - 1;
    else if (target > arr[mid2]) lo = mid2 + 1;
    else { lo = mid1 + 1; hi = mid2 - 1; }
  }
  return -1;
}
