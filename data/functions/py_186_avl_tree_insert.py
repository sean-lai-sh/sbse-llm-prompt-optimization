from typing import List, Optional


def avl_tree_insert(values: List[int]) -> List[int]:
    class Node:
        def __init__(self, val: int) -> None:
            self.val = val
            self.left: Optional["Node"] = None
            self.right: Optional["Node"] = None
            self.height = 1

    def height(node: Optional[Node]) -> int:
        return node.height if node else 0

    def update_height(node: Node) -> None:
        node.height = 1 + max(height(node.left), height(node.right))

    def balance_factor(node: Node) -> int:
        return height(node.left) - height(node.right)

    def rotate_right(y: Node) -> Node:
        x = y.left
        assert x is not None
        t = x.right
        x.right = y
        y.left = t
        update_height(y)
        update_height(x)
        return x

    def rotate_left(x: Node) -> Node:
        y = x.right
        assert y is not None
        t = y.left
        y.left = x
        x.right = t
        update_height(x)
        update_height(y)
        return y

    def insert(node: Optional[Node], val: int) -> Node:
        if node is None:
            return Node(val)
        if val < node.val:
            node.left = insert(node.left, val)
        elif val > node.val:
            node.right = insert(node.right, val)
        else:
            return node
        update_height(node)
        bf = balance_factor(node)
        if bf > 1:
            assert node.left is not None
            if val < node.left.val:
                return rotate_right(node)
            node.left = rotate_left(node.left)
            return rotate_right(node)
        if bf < -1:
            assert node.right is not None
            if val > node.right.val:
                return rotate_left(node)
            node.right = rotate_right(node.right)
            return rotate_left(node)
        return node

    def inorder(node: Optional[Node], result: List[int]) -> None:
        if node is None:
            return
        inorder(node.left, result)
        result.append(node.val)
        inorder(node.right, result)

    root: Optional[Node] = None
    for v in values:
        root = insert(root, v)
    result: List[int] = []
    inorder(root, result)
    return result
