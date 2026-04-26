function countingSortByDigit(arr: number[], exp: number): number[] {
  const n = arr.length;
  const output = new Array<number>(n).fill(0);
  const count = new Array<number>(10).fill(0);
  for (let i = 0; i < n; i++) count[Math.floor(arr[i] / exp) % 10]++;
  for (let i = 1; i < 10; i++) count[i] += count[i - 1];
  for (let i = n - 1; i >= 0; i--) {
    const digit = Math.floor(arr[i] / exp) % 10;
    output[count[digit] - 1] = arr[i];
    count[digit]--;
  }
  return output;
}

export function radixSort(arr: number[]): number[] {
  if (arr.length === 0) return [];
  let a = [...arr];
  const max = Math.max(...a);
  for (let exp = 1; Math.floor(max / exp) > 0; exp *= 10) {
    a = countingSortByDigit(a, exp);
  }
  return a;
}
