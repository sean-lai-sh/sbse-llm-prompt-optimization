def string_to_int_manual(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("empty string")
    negative = s[0] == '-'
    digits = s[1:] if s[0] in '+-' else s
    result = 0
    for ch in digits:
        if not ch.isdigit():
            raise ValueError(f"invalid character: {ch!r}")
        result = result * 10 + (ord(ch) - ord('0'))
    return -result if negative else result
