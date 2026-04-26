export function shellSort(arr: number[]): number[] {
  const a = [...arr];
  const n = a.length;
  let gap = Math.floor(n / 2);

  while (gap > 0) {
    for (let i = gap; i < n; i++) {
      const temp = a[i];
      let j = i;
      while (j >= gap && a[j - gap] > temp) {
        a[j] = a[j - gap];
        j -= gap;
      }
      a[j] = temp;
    }
    gap = Math.floor(gap / 2);
  }
  return a;
}
