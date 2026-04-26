from typing import List


def collatz(n: int) -> List[int]:
    if n <= 0:
        raise ValueError("n must be a positive integer")
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence
