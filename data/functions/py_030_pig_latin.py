def pig_latin(word: str) -> str:
    vowels = 'aeiouAEIOU'
    if word[0] in vowels:
        return word + 'way'
    i = 0
    while i < len(word) and word[i] not in vowels:
        i += 1
    return word[i:] + word[:i] + 'ay'
