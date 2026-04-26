from typing import List, Union


def run_length_encode_advanced(data: List[int]) -> List[Union[int, List[int]]]:
    if not data:
        return []

    result: List[Union[int, List[int]]] = []
    i = 0
    n = len(data)

    while i < n:
        run_start = i
        while i + 1 < n and data[i + 1] == data[run_start]:
            i += 1
        run_len = i - run_start + 1

        if run_len >= 3:
            result.append([run_len, data[run_start]])
            i += 1
            continue

        literal_start = i
        i += 1
        while i < n:
            if i + 2 < n and data[i] == data[i + 1] == data[i + 2]:
                break
            i += 1

        literal_block = data[literal_start:i]
        if len(literal_block) == 1:
            result.append(literal_block[0])
        else:
            for val in literal_block:
                result.append(val)

    return result
