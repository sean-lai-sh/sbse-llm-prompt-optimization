def int_to_string_manual(n: int) -> str:
    if n == 0:
        return "0"
    negative = n < 0
    n = abs(n)
    digits = []
    while n > 0:
        digits.append(chr(ord('0') + n % 10))
        n //= 10
    if negative:
        digits.append('-')
    return "".join(reversed(digits))
