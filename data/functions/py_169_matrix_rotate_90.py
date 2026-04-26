from typing import List


def matrix_rotate_90(matrix: List[List[int]]) -> List[List[int]]:
    if not matrix or not matrix[0]:
        return []
    n = len(matrix)
    m = len(matrix[0])
    rotated = [[0] * n for _ in range(m)]
    for r in range(n):
        for c in range(m):
            rotated[c][n - 1 - r] = matrix[r][c]
    return rotated
