export function floorDiv(a: number, b: number): number {
  if (b === 0) throw new Error("division by zero");
  return Math.floor(a / b);
}
