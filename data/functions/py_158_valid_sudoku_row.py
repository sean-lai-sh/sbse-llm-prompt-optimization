from typing import List


def valid_sudoku_row(row: List[int]) -> bool:
    seen = set()
    for val in row:
        if val == 0:
            continue
        if val < 1 or val > 9:
            return False
        if val in seen:
            return False
        seen.add(val)
    return True
