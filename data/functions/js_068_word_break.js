export default function wordBreak(s, wordDict) {
  const wordSet = new Set(wordDict);
  const n = s.length;

  // dp[i] = true if s.substring(0, i) can be segmented
  const dp = new Array(n + 1).fill(false);
  dp[0] = true;

  // Also track the actual segmentation
  const prev = new Array(n + 1).fill(-1);

  for (let i = 1; i <= n; i++) {
    for (let j = 0; j < i; j++) {
      if (dp[j] && wordSet.has(s.substring(j, i))) {
        dp[i] = true;
        prev[i] = j;
        break;
      }
    }
  }

  if (!dp[n]) {
    return { canBreak: false, segments: [] };
  }

  // Reconstruct the segmentation
  const segments = [];
  let idx = n;
  while (idx > 0) {
    const start = prev[idx];
    segments.unshift(s.substring(start, idx));
    idx = start;
  }

  return { canBreak: true, segments };
}
