interface ZResult {
  zArray: number[];
  matches: number[];
}

export function zAlgorithm(text: string, pattern: string): ZResult {
  const concat = pattern + "$" + text;
  const n = concat.length;
  const zArray: number[] = new Array(n).fill(0);
  const matches: number[] = [];

  let l = 0;
  let r = 0;

  for (let i = 1; i < n; i++) {
    if (i < r) {
      zArray[i] = Math.min(r - i, zArray[i - l]);
    }
    while (i + zArray[i] < n && concat[zArray[i]] === concat[i + zArray[i]]) {
      zArray[i]++;
    }
    if (i + zArray[i] > r) {
      l = i;
      r = i + zArray[i];
    }
  }

  // Find pattern matches in text (offset by pattern.length + 1)
  const offset = pattern.length + 1;
  for (let i = offset; i < n; i++) {
    if (zArray[i] === pattern.length) {
      matches.push(i - offset);
    }
  }

  return { zArray: zArray.slice(offset), matches };
}
