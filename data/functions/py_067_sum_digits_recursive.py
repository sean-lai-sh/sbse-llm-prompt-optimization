def sum_digits_recursive(n: int) -> int:
    n = abs(n)
    if n < 10:
        return n
    return n % 10 + sum_digits_recursive(n // 10)
