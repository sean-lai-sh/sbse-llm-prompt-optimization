from typing import List, Optional


def matrix_multiply(
    a: List[List[float]],
    b: List[List[float]],
    mod: Optional[int] = None
) -> List[List[float]]:
    if not a or not b:
        raise ValueError("Matrices cannot be empty")

    rows_a = len(a)
    cols_a = len(a[0])
    rows_b = len(b)
    cols_b = len(b[0])

    if cols_a != rows_b:
        raise ValueError(
            f"Incompatible dimensions: ({rows_a}x{cols_a}) x ({rows_b}x{cols_b})"
        )

    for i, row in enumerate(a):
        if len(row) != cols_a:
            raise ValueError(f"Matrix A row {i} has inconsistent length")
    for i, row in enumerate(b):
        if len(row) != cols_b:
            raise ValueError(f"Matrix B row {i} has inconsistent length")

    result = [[0.0] * cols_b for _ in range(rows_a)]

    for i in range(rows_a):
        for k in range(cols_a):
            if a[i][k] == 0:
                continue
            for j in range(cols_b):
                result[i][j] += a[i][k] * b[k][j]

    if mod is not None:
        for i in range(rows_a):
            for j in range(cols_b):
                result[i][j] = result[i][j] % mod

    return result
