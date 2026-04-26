def permutations(n: int, r: int) -> int:
    if r < 0 or r > n:
        return 0
    result = 1
    for i in range(n, n - r, -1):
        result *= i
    return result
