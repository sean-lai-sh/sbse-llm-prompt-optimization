/**
 * Word Break problem: determine if `s` can be segmented into a sequence of
 * dictionary words.  Returns true/false and one valid segmentation if found.
 */
export interface WordBreakResult {
  canBreak: boolean;
  segments: string[];
}

export function wordBreak(s: string, wordDict: string[]): WordBreakResult {
  const n = s.length;
  const wordSet = new Set(wordDict);

  // dp[i] = true if s[0..i-1] can be segmented
  const dp = new Array<boolean>(n + 1).fill(false);
  // predecessor: from which position we jumped to i
  const pred = new Array<number>(n + 1).fill(-1);
  dp[0] = true;

  for (let i = 1; i <= n; i++) {
    for (let j = 0; j < i; j++) {
      if (dp[j] && wordSet.has(s.slice(j, i))) {
        dp[i] = true;
        pred[i] = j;
        break;
      }
    }
  }

  if (!dp[n]) return { canBreak: false, segments: [] };

  // Reconstruct segmentation
  const segments: string[] = [];
  let pos = n;
  while (pos > 0) {
    const from = pred[pos];
    segments.push(s.slice(from, pos));
    pos = from;
  }
  segments.reverse();

  return { canBreak: true, segments };
}
