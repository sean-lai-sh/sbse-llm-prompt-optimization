export function mod(a: number, b: number): number {
  if (b === 0) throw new Error("modulo by zero");
  return ((a % b) + b) % b;
}
