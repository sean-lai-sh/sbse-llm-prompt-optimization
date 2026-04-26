def abbreviate(phrase: str) -> str:
    words = phrase.strip().split()
    return ''.join(word[0].upper() for word in words if word)
