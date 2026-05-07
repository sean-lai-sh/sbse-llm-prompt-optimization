export function parityFlag(n: number): "even" | "odd" {
  return n % 2 === 0 ? "even" : "odd";
}
