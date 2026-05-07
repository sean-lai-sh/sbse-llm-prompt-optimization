def decimal_to_binary(n: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    bits: list[str] = []
    while n:
        bits.append(str(n & 1))
        n >>= 1
    return sign + "".join(reversed(bits))
