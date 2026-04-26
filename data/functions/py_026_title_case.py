def title_case(s: str) -> str:
    minor_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on',
                   'at', 'to', 'by', 'in', 'of', 'up', 'as'}
    words = s.lower().split()
    result = []
    for i, word in enumerate(words):
        if i == 0 or word not in minor_words:
            result.append(word.capitalize())
        else:
            result.append(word)
    return ' '.join(result)
