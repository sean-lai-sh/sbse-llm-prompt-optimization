def roman_numeral_add(a: str, b: str) -> str:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    def to_int(s: str) -> int:
        total = 0
        prev = 0
        for ch in reversed(s.upper()):
            v = values[ch]
            total += -v if v < prev else v
            prev = v
        return total

    def to_roman(n: int) -> str:
        symbols = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ]
        out = []
        for value, sym in symbols:
            while n >= value:
                out.append(sym)
                n -= value
        return "".join(out)

    return to_roman(to_int(a) + to_int(b))
