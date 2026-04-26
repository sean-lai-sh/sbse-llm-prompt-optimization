interface KMPResult {
  matches: number[];
  lps: number[];
}

export function kmpSearch(text: string, pattern: string): KMPResult {
  const n = text.length;
  const m = pattern.length;
  const matches: number[] = [];

  if (m === 0) return { matches, lps: [] };

  // Build LPS (Longest Proper Prefix which is also Suffix) array
  const lps: number[] = new Array(m).fill(0);
  let len = 0;
  let i = 1;

  while (i < m) {
    if (pattern[i] === pattern[len]) {
      lps[i++] = ++len;
    } else if (len !== 0) {
      len = lps[len - 1];
    } else {
      lps[i++] = 0;
    }
  }

  // KMP matching
  i = 0; // index for text
  let j = 0; // index for pattern

  while (i < n) {
    if (text[i] === pattern[j]) {
      i++;
      j++;
    }
    if (j === m) {
      matches.push(i - j); // found match at index i - j
      j = lps[j - 1];
    } else if (i < n && text[i] !== pattern[j]) {
      if (j !== 0) {
        j = lps[j - 1];
      } else {
        i++;
      }
    }
  }

  return { matches, lps };
}
