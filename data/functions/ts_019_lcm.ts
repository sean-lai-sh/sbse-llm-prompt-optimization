export function lcm(a: number, b: number): number {
  if (a === 0 || b === 0) return 0;
  const absA = Math.abs(a), absB = Math.abs(b);
  let g = absA, r = absB;
  while (r !== 0) [g, r] = [r, g % r];
  return (absA / g) * absB;
}
