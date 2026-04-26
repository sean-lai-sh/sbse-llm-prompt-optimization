def is_perfect(n: int) -> bool:
    if n < 2:
        return False
    total = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total == n
