def power_recursive(base: float, exp: int) -> float:
    if exp == 0:
        return 1.0
    if exp < 0:
        return 1.0 / power_recursive(base, -exp)
    if exp % 2 == 0:
        half = power_recursive(base, exp // 2)
        return half * half
    return base * power_recursive(base, exp - 1)
