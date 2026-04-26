export default function validParenthesisLength(s) {
  // Returns the length of the longest valid parenthesis substring
  const n = s.length;
  if (n === 0) return 0;

  // dp[i] = length of longest valid parens ending at index i
  const dp = new Array(n).fill(0);
  let maxLen = 0;

  for (let i = 1; i < n; i++) {
    if (s[i] === ')') {
      if (s[i - 1] === '(') {
        // Direct match: "()"
        dp[i] = (i >= 2 ? dp[i - 2] : 0) + 2;
      } else if (dp[i - 1] > 0) {
        // Check if there is a matching '(' before the valid substring
        const matchIdx = i - dp[i - 1] - 1;
        if (matchIdx >= 0 && s[matchIdx] === '(') {
          dp[i] = dp[i - 1] + 2;
          // Add the valid substring before the matched '('
          if (matchIdx > 0) {
            dp[i] += dp[matchIdx - 1];
          }
        }
      }
      maxLen = Math.max(maxLen, dp[i]);
    }
  }

  return maxLen;
}
