from typing import List


def transpose_matrix(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix or not matrix[0]:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]
