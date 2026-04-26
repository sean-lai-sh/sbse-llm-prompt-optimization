def power(base: float, exp: int) -> float:
    if exp == 0:
        return 1.0
    if exp < 0:
        return 1.0 / power(base, -exp)
    result = 1.0
    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2
    return result
