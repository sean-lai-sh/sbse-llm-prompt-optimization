def gcd_recursive(a: int, b: int) -> int:
    if b == 0:
        return abs(a)
    return gcd_recursive(b, a % b)
