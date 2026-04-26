export function sumOfDigits(n: number): number {
  return String(Math.abs(n)).split("").reduce((sum, d) => sum + Number(d), 0);
}
