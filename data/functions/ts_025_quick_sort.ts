function partition(a: number[], lo: number, hi: number): number {
  const pivot = a[hi];
  let i = lo - 1;
  for (let j = lo; j < hi; j++) {
    if (a[j] <= pivot) {
      i++;
      [a[i], a[j]] = [a[j], a[i]];
    }
  }
  [a[i + 1], a[hi]] = [a[hi], a[i + 1]];
  return i + 1;
}

function qs(a: number[], lo: number, hi: number): void {
  if (lo < hi) {
    const p = partition(a, lo, hi);
    qs(a, lo, p - 1);
    qs(a, p + 1, hi);
  }
}

export function quickSort(arr: number[]): number[] {
  const a = [...arr];
  qs(a, 0, a.length - 1);
  return a;
}
