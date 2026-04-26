def rot13(text: str) -> str:
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + 13) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)
