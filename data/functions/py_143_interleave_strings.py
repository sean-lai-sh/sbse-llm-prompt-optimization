def interleave_strings(s1: str, s2: str) -> str:
    result = []
    i, j = 0, 0
    while i < len(s1) and j < len(s2):
        result.append(s1[i])
        result.append(s2[j])
        i += 1
        j += 1
    result.append(s1[i:])
    result.append(s2[j:])
    return "".join(result)
