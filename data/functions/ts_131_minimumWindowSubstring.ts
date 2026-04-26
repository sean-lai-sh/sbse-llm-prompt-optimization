export function minimumWindowSubstring(s: string, t: string): string {
  if (t.length === 0) return "";
  const need = new Map<string, number>();
  for (const ch of t) need.set(ch, (need.get(ch) ?? 0) + 1);

  let have = 0;
  const required = need.size;
  const window = new Map<string, number>();
  let minLen = Infinity;
  let minStart = 0;
  let left = 0;

  for (let right = 0; right < s.length; right++) {
    const ch = s[right];
    window.set(ch, (window.get(ch) ?? 0) + 1);
    if (need.has(ch) && window.get(ch) === need.get(ch)) have++;

    while (have === required) {
      if (right - left + 1 < minLen) {
        minLen = right - left + 1;
        minStart = left;
      }
      const leftCh = s[left];
      window.set(leftCh, (window.get(leftCh) ?? 0) - 1);
      if (need.has(leftCh) && (window.get(leftCh) ?? 0) < (need.get(leftCh) ?? 0)) have--;
      left++;
    }
  }

  return minLen === Infinity ? "" : s.slice(minStart, minStart + minLen);
}
