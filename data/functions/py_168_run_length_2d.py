from typing import List, Tuple


def run_length_2d(matrix: List[List[int]]) -> List[Tuple[int, int]]:
    result: List[Tuple[int, int]] = []
    if not matrix or not matrix[0]:
        return result
    flat = [val for row in matrix for val in row]
    if not flat:
        return result
    current = flat[0]
    count = 1
    for val in flat[1:]:
        if val == current:
            count += 1
        else:
            result.append((current, count))
            current = val
            count = 1
    result.append((current, count))
    return result
