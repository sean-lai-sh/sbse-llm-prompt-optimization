from typing import List, Tuple


def tower_of_hanoi(n: int, source: str = 'A', target: str = 'C', auxiliary: str = 'B') -> List[Tuple[str, str]]:
    moves: List[Tuple[str, str]] = []
    if n == 1:
        moves.append((source, target))
        return moves
    moves.extend(tower_of_hanoi(n - 1, source, auxiliary, target))
    moves.append((source, target))
    moves.extend(tower_of_hanoi(n - 1, auxiliary, target, source))
    return moves
