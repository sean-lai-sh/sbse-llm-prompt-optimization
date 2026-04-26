def sum_digits(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))
