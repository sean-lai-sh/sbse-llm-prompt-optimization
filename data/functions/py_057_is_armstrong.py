def is_armstrong(n: int) -> bool:
    digits = str(abs(n))
    power = len(digits)
    return sum(int(d) ** power for d in digits) == abs(n)
