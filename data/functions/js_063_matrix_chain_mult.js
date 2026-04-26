export default function matrixChainMult(dimensions) {
  // dimensions[i] x dimensions[i+1] is the size of matrix i
  const n = dimensions.length - 1; // number of matrices
  if (n <= 0) return { minOps: 0, order: '' };
  if (n === 1) return { minOps: 0, order: 'A' };

  // dp[i][j] = min operations to multiply matrices i through j (0-indexed)
  const dp = Array.from({ length: n }, () => new Array(n).fill(0));
  // split[i][j] = optimal split point
  const split = Array.from({ length: n }, () => new Array(n).fill(0));

  // l is the chain length
  for (let l = 2; l <= n; l++) {
    for (let i = 0; i <= n - l; i++) {
      const j = i + l - 1;
      dp[i][j] = Infinity;
      for (let k = i; k < j; k++) {
        const cost =
          dp[i][k] +
          dp[k + 1][j] +
          dimensions[i] * dimensions[k + 1] * dimensions[j + 1];
        if (cost < dp[i][j]) {
          dp[i][j] = cost;
          split[i][j] = k;
        }
      }
    }
  }

  function buildOrder(i, j) {
    if (i === j) return String.fromCharCode(65 + i); // 'A', 'B', etc.
    const k = split[i][j];
    const left = buildOrder(i, k);
    const right = buildOrder(k + 1, j);
    return `(${left}${right})`;
  }

  return { minOps: dp[0][n - 1], order: buildOrder(0, n - 1) };
}
