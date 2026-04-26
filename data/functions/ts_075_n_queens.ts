export interface QueenPosition {
  row: number;
  col: number;
}

export interface NQueensResult {
  totalSolutions: number;
  solutions: QueenPosition[][];
}

/**
 * N-Queens Problem.
 * Place N queens on an N×N chessboard so that no two queens attack each other.
 * Returns all distinct solutions, each solution being an array of queen positions.
 */
export function nQueens(n: number): NQueensResult {
  if (n <= 0) throw new RangeError("n must be a positive integer");

  const solutions: QueenPosition[][] = [];

  // Track which columns and diagonals are occupied
  const cols = new Set<number>();
  const diag1 = new Set<number>(); // row - col
  const diag2 = new Set<number>(); // row + col

  const current: QueenPosition[] = [];

  function backtrack(row: number): void {
    if (row === n) {
      solutions.push(current.map((p) => ({ ...p })));
      return;
    }

    for (let col = 0; col < n; col++) {
      const d1 = row - col;
      const d2 = row + col;

      if (cols.has(col) || diag1.has(d1) || diag2.has(d2)) continue;

      // Place queen
      cols.add(col);
      diag1.add(d1);
      diag2.add(d2);
      current.push({ row, col });

      backtrack(row + 1);

      // Remove queen
      cols.delete(col);
      diag1.delete(d1);
      diag2.delete(d2);
      current.pop();
    }
  }

  backtrack(0);

  return { totalSolutions: solutions.length, solutions };
}
