export function isAnagram(a: string, b: string): boolean {
  const normalize = (s: string): string =>
    s.toLowerCase().replace(/\s/g, "").split("").sort().join("");
  return normalize(a) === normalize(b);
}
