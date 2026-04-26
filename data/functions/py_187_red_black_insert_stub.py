from typing import List, Optional

RED = True
BLACK = False


def red_black_insert_stub(values: List[int]) -> List[int]:
    class Node:
        def __init__(self, val: int) -> None:
            self.val = val
            self.color = RED
            self.left: Optional["Node"] = None
            self.right: Optional["Node"] = None

    def is_red(node: Optional[Node]) -> bool:
        return node is not None and node.color == RED

    def rotate_left(h: Node) -> Node:
        x = h.right
        assert x is not None
        h.right = x.left
        x.left = h
        x.color = h.color
        h.color = RED
        return x

    def rotate_right(h: Node) -> Node:
        x = h.left
        assert x is not None
        h.left = x.right
        x.right = h
        x.color = h.color
        h.color = RED
        return x

    def flip_colors(h: Node) -> None:
        h.color = RED
        if h.left:
            h.left.color = BLACK
        if h.right:
            h.right.color = BLACK

    def insert(h: Optional[Node], val: int) -> Node:
        if h is None:
            return Node(val)
        if val < h.val:
            h.left = insert(h.left, val)
        elif val > h.val:
            h.right = insert(h.right, val)
        if is_red(h.right) and not is_red(h.left):
            h = rotate_left(h)
        if is_red(h.left) and h.left and is_red(h.left.left):
            h = rotate_right(h)
        if is_red(h.left) and is_red(h.right):
            flip_colors(h)
        return h

    def inorder(node: Optional[Node], result: List[int]) -> None:
        if node is None:
            return
        inorder(node.left, result)
        result.append(node.val)
        inorder(node.right, result)

    root: Optional[Node] = None
    for v in values:
        root = insert(root, v)
    if root:
        root.color = BLACK
    result: List[int] = []
    inorder(root, result)
    return result
