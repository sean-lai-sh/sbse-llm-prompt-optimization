import string


def strip_punctuation(s: str) -> str:
    return s.translate(str.maketrans("", "", string.punctuation))
