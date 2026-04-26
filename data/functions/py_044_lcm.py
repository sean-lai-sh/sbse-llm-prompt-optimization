def lcm(a: int, b: int) -> int:
    def gcd(x: int, y: int) -> int:
        while y:
            x, y = y, x % y
        return abs(x)
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)
