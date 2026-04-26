export function mostFrequentChar(s: string): string {
  if (s.length === 0) throw new RangeError("String must not be empty");
  const freq = new Map<string, number>();
  for (const ch of s) {
    freq.set(ch, (freq.get(ch) ?? 0) + 1);
  }
  let maxCh = s[0];
  let maxCount = 0;
  for (const [ch, count] of freq) {
    if (count > maxCount) { maxCount = count; maxCh = ch; }
  }
  return maxCh;
}
