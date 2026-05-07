def count_set_bits(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
