export function rotateMatrix(matrix: number[][]): number[][] {
  const n = matrix.length;
  if (n === 0) return [];
  const result: number[][] = Array.from({ length: n }, () => Array(n).fill(0));
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      result[c][n - 1 - r] = matrix[r][c];
    }
  }
  return result;
}
