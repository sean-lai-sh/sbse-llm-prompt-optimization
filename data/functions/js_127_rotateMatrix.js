export default function rotateMatrix(matrix) {
  // Rotate 90 degrees clockwise in-place
  const n = matrix.length;
  if (n === 0) return matrix;
  // Transpose
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]];
    }
  }
  // Reverse each row
  for (let i = 0; i < n; i++) {
    matrix[i].reverse();
  }
  return matrix;
}
