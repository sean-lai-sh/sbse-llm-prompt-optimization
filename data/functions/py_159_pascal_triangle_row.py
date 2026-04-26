from typing import List


def pascal_triangle_row(n: int) -> List[int]:
    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row
