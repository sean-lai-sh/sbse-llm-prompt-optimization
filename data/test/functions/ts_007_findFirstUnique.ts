export function findFirstUnique<T>(arr: T[]): T | undefined {
  const counts = new Map<T, number>();
  for (const item of arr) {
    counts.set(item, (counts.get(item) ?? 0) + 1);
  }
  for (const item of arr) {
    if (counts.get(item) === 1) return item;
  }
  return undefined;
}
