type Board = string[][];

interface NQueensResult {
  solutions: Board[];
  count: number;
}

export function nQueens(n: number): NQueensResult {
  const solutions: Board[] = [];

  // Track occupied columns and diagonals
  const cols = new Set<number>();
  const diag1 = new Set<number>(); // row - col
  const diag2 = new Set<number>(); // row + col

  const board: number[] = new Array(n).fill(-1); // board[row] = col of queen

  const formatBoard = (): Board => {
    return board.map((queenCol) =>
      Array.from({ length: n }, (_, c) => (c === queenCol ? "Q" : "."))
    );
  };

  const backtrack = (row: number): void => {
    if (row === n) {
      solutions.push(formatBoard());
      return;
    }

    for (let col = 0; col < n; col++) {
      if (cols.has(col) || diag1.has(row - col) || diag2.has(row + col)) {
        continue; // This position is under attack
      }

      // Place queen
      board[row] = col;
      cols.add(col);
      diag1.add(row - col);
      diag2.add(row + col);

      backtrack(row + 1);

      // Remove queen (backtrack)
      board[row] = -1;
      cols.delete(col);
      diag1.delete(row - col);
      diag2.delete(row + col);
    }
  };

  if (n > 0) backtrack(0);

  return { solutions, count: solutions.length };
}
