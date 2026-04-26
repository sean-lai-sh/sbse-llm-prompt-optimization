export function groupAndCount<T>(arr: T[], key: keyof T): Record<string, number> {
  const result: Record<string, number> = {};
  for (const item of arr) {
    const groupKey = String(item[key]);
    result[groupKey] = (result[groupKey] ?? 0) + 1;
  }
  return result;
}
