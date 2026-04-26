def digital_root(n: int) -> int:
    n = abs(n)
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n
