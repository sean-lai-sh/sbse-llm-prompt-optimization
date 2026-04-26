def palindrome_recursive(s: str) -> bool:
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    if len(cleaned) <= 1:
        return True
    if cleaned[0] != cleaned[-1]:
        return False
    return palindrome_recursive(cleaned[1:-1])
