from typing import Any, Dict, List, Optional


def binary_tree_ops(
    operation: str,
    root: Optional[Dict[str, Any]],
    value: Optional[Any] = None
) -> Any:
    def insert(node: Optional[Dict], val: Any) -> Dict:
        if node is None:
            return {'value': val, 'left': None, 'right': None}
        if val < node['value']:
            node['left'] = insert(node['left'], val)
        elif val > node['value']:
            node['right'] = insert(node['right'], val)
        return node

    def search(node: Optional[Dict], val: Any) -> bool:
        if node is None:
            return False
        if val == node['value']:
            return True
        if val < node['value']:
            return search(node['left'], val)
        return search(node['right'], val)

    def inorder(node: Optional[Dict]) -> List[Any]:
        if node is None:
            return []
        return inorder(node['left']) + [node['value']] + inorder(node['right'])

    def height(node: Optional[Dict]) -> int:
        if node is None:
            return 0
        return 1 + max(height(node['left']), height(node['right']))

    def min_node(node: Dict) -> Dict:
        while node['left'] is not None:
            node = node['left']
        return node

    def delete(node: Optional[Dict], val: Any) -> Optional[Dict]:
        if node is None:
            return None
        if val < node['value']:
            node['left'] = delete(node['left'], val)
        elif val > node['value']:
            node['right'] = delete(node['right'], val)
        else:
            if node['left'] is None:
                return node['right']
            if node['right'] is None:
                return node['left']
            successor = min_node(node['right'])
            node['value'] = successor['value']
            node['right'] = delete(node['right'], successor['value'])
        return node

    if operation == 'insert':
        return insert(root, value)
    elif operation == 'search':
        return search(root, value)
    elif operation == 'inorder':
        return inorder(root)
    elif operation == 'height':
        return height(root)
    elif operation == 'delete':
        return delete(root, value)
    else:
        raise ValueError(f"Unknown operation: {operation}")
