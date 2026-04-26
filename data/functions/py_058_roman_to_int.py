def roman_to_int(s: str) -> int:
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
              'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev = 0
    for ch in reversed(s.upper()):
        curr = values[ch]
        if curr < prev:
            result -= curr
        else:
            result += curr
        prev = curr
    return result
