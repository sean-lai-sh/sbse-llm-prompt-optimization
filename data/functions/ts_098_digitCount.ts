export function digitCount(n: number): number {
  return String(Math.abs(n === 0 ? 0 : n)).replace(".", "").length;
}
