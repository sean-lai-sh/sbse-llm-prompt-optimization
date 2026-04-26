export function flattenDeep<T>(arr: unknown[]): T[] {
  const result: T[] = [];
  function recurse(a: unknown[]): void {
    for (const item of a) {
      if (Array.isArray(item)) recurse(item);
      else result.push(item as T);
    }
  }
  recurse(arr);
  return result;
}
