export function factorial(n: number): number {
  if (n < 0) throw new RangeError("n must be non-negative");
  return n <= 1 ? 1 : n * factorial(n - 1);
}
