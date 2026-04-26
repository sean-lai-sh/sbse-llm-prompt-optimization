export default function zAlgorithm(text, pattern) {
  // Z-Algorithm for pattern matching
  // Returns all starting indices where pattern occurs in text
  // Also returns the raw Z-array of the concatenated string

  if (!pattern || pattern.length === 0) return { matches: [], zArray: [] };
  if (!text || text.length === 0) return { matches: [], zArray: [] };

  const separator = "$";
  const concat = pattern + separator + text;
  const n = concat.length;
  const z = new Array(n).fill(0);
  z[0] = n;

  let l = 0;
  let r = 0;
  for (let i = 1; i < n; i++) {
    if (i < r) {
      z[i] = Math.min(r - i, z[i - l]);
    }
    while (i + z[i] < n && concat[z[i]] === concat[i + z[i]]) {
      z[i]++;
    }
    if (i + z[i] > r) {
      l = i;
      r = i + z[i];
    }
  }

  const patLen = pattern.length;
  const matches = [];
  for (let i = patLen + 1; i < n; i++) {
    if (z[i] === patLen) {
      matches.push(i - patLen - 1);
    }
  }

  // Also expose pure Z-array computation for the input string alone
  function computeZ(s) {
    const zArr = new Array(s.length).fill(0);
    zArr[0] = s.length;
    let lo = 0, ro = 0;
    for (let i = 1; i < s.length; i++) {
      if (i < ro) zArr[i] = Math.min(ro - i, zArr[i - lo]);
      while (i + zArr[i] < s.length && s[zArr[i]] === s[i + zArr[i]]) zArr[i]++;
      if (i + zArr[i] > ro) { lo = i; ro = i + zArr[i]; }
    }
    return zArr;
  }

  return {
    matches,
    zArray: computeZ(text),
    concatZArray: z,
  };
}
