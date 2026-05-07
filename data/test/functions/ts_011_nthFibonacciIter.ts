export function nthFibonacciIter(n: number): number {
  if (n < 0) throw new Error("n must be non-negative");
  if (n < 2) return n;
  let a = 0;
  let b = 1;
  for (let i = 2; i <= n; i += 1) {
    const next = a + b;
    a = b;
    b = next;
  }
  return b;
}
