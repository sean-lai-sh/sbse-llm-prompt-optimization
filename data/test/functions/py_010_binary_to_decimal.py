def binary_to_decimal(bits: str) -> int:
    if not bits:
        raise ValueError("empty input")
    negative = False
    if bits.startswith("-"):
        negative = True
        bits = bits[1:]
    value = 0
    for ch in bits:
        if ch not in "01":
            raise ValueError(f"invalid bit: {ch!r}")
        value = (value << 1) | (1 if ch == "1" else 0)
    return -value if negative else value
