from typing import List, Optional, Tuple


def maximal_square(
    matrix: List[List[str]],
    return_position: bool = False
) -> Tuple[int, Optional[Tuple[int, int]]]:
    if not matrix or not matrix[0]:
        return (0, None)

    rows = len(matrix)
    cols = len(matrix[0])

    for i, row in enumerate(matrix):
        if len(row) != cols:
            raise ValueError(f"Row {i} has inconsistent length")
        for j, cell in enumerate(row):
            if cell not in ('0', '1', 0, 1):
                raise ValueError(f"Invalid cell value at ({i},{j}): {cell!r}")

    dp = [[0] * cols for _ in range(rows)]
    max_side = 0
    max_pos: Optional[Tuple[int, int]] = None

    for i in range(rows):
        for j in range(cols):
            cell_val = str(matrix[i][j])
            if cell_val == '1':
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

                if dp[i][j] > max_side:
                    max_side = dp[i][j]
                    if return_position:
                        max_pos = (i - max_side + 1, j - max_side + 1)

    area = max_side * max_side
    if return_position:
        return (area, max_pos)
    return (area, None)
