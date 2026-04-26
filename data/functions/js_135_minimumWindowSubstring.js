export default function minimumWindowSubstring(s, t) {
  if (!s || !t || s.length < t.length) return "";
  const need = {};
  for (const ch of t) need[ch] = (need[ch] || 0) + 1;
  const window = {};
  let have = 0, required = Object.keys(need).length;
  let left = 0, minLen = Infinity, minLeft = 0;
  for (let right = 0; right < s.length; right++) {
    const ch = s[right];
    window[ch] = (window[ch] || 0) + 1;
    if (need[ch] !== undefined && window[ch] === need[ch]) have++;
    while (have === required) {
      if (right - left + 1 < minLen) {
        minLen = right - left + 1;
        minLeft = left;
      }
      const leftCh = s[left];
      window[leftCh]--;
      if (need[leftCh] !== undefined && window[leftCh] < need[leftCh]) have--;
      left++;
    }
  }
  return minLen === Infinity ? "" : s.slice(minLeft, minLeft + minLen);
}
