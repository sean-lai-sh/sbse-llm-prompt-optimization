export function snakeToCamel(s: string): string {
  return s
    .toLowerCase()
    .replace(/_([a-z])/g, (_, ch: string) => ch.toUpperCase());
}
