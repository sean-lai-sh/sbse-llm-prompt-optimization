export function isAnagramSimple(a: string, b: string): boolean {
  const normalize = (s: string): string => s.toLowerCase().split("").sort().join("");
  return normalize(a) === normalize(b);
}
