export default function matrixMultiply(A, B) {
  const rowsA = A.length;
  const colsA = A[0].length;
  const colsB = B[0].length;
  if (colsA !== B.length) throw new Error("Incompatible matrix dimensions");
  const C = Array.from({ length: rowsA }, () => Array(colsB).fill(0));
  for (let i = 0; i < rowsA; i++) {
    for (let j = 0; j < colsB; j++) {
      for (let k = 0; k < colsA; k++) {
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
  return C;
}
