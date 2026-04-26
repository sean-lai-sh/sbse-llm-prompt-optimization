export function sortByKey<T>(arr: T[], key: keyof T, asc: boolean = true): T[] {
  return [...arr].sort((a, b) => {
    const valA = a[key];
    const valB = b[key];
    if (valA < valB) return asc ? -1 : 1;
    if (valA > valB) return asc ? 1 : -1;
    return 0;
  });
}
