from typing import Optional


def tree_height(node: Optional[dict]) -> int:
    if node is None:
        return 0
    left_height = tree_height(node.get('left'))
    right_height = tree_height(node.get('right'))
    return 1 + max(left_height, right_height)
