export function kmpFailureTable(pattern: string): number[] {
  const table = new Array<number>(pattern.length).fill(0);
  let len = 0;
  let i = 1;
  while (i < pattern.length) {
    if (pattern[i] === pattern[len]) {
      len += 1;
      table[i] = len;
      i += 1;
    } else if (len !== 0) {
      len = table[len - 1];
    } else {
      table[i] = 0;
      i += 1;
    }
  }
  return table;
}
