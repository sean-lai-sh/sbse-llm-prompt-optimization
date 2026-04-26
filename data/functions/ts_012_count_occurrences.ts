export function countOccurrences<T>(arr: T[], val: T): number {
  return arr.reduce((count, item) => (item === val ? count + 1 : count), 0);
}
