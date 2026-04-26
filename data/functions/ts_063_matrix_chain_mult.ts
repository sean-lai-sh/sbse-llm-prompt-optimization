export interface MatrixChainResult {
  minOperations: number;
  optimalParenthesization: string;
}

/**
 * Matrix Chain Multiplication: find the minimum number of scalar multiplications
 * needed to compute the product of a chain of matrices.
 * `dims[i]` and `dims[i+1]` are the dimensions of the i-th matrix.
 */
export function matrixChainMult(dims: number[]): MatrixChainResult {
  const n = dims.length - 1; // number of matrices
  if (n <= 0) throw new RangeError("Need at least one matrix");

  // m[i][j] = min cost to multiply matrices i..j (0-indexed)
  const m: number[][] = Array.from({ length: n }, () =>
    new Array<number>(n).fill(0)
  );
  // s[i][j] = split point that achieves the minimum
  const s: number[][] = Array.from({ length: n }, () =>
    new Array<number>(n).fill(0)
  );

  for (let len = 2; len <= n; len++) {
    for (let i = 0; i <= n - len; i++) {
      const j = i + len - 1;
      m[i][j] = Infinity;
      for (let k = i; k < j; k++) {
        const cost = m[i][k] + m[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1];
        if (cost < m[i][j]) {
          m[i][j] = cost;
          s[i][j] = k;
        }
      }
    }
  }

  function buildParens(i: number, j: number): string {
    if (i === j) return `M${i + 1}`;
    return `(${buildParens(i, s[i][j])} x ${buildParens(s[i][j] + 1, j)})`;
  }

  return {
    minOperations: m[0][n - 1],
    optimalParenthesization: buildParens(0, n - 1),
  };
}
