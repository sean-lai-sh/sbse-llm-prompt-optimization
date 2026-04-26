export function flattenOnce<T>(arr: T[][]): T[] {
  return ([] as T[]).concat(...arr);
}
