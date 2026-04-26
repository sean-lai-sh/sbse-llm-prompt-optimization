from typing import Any, Callable, Dict, List, Optional


def pivot_table(
    data: List[Dict[str, Any]],
    index: str,
    columns: str,
    values: str,
    aggfunc: Optional[Callable[[List[Any]], Any]] = None
) -> Dict[Any, Dict[Any, Any]]:
    if aggfunc is None:
        aggfunc = lambda x: sum(x) / len(x) if x else None
    raw: Dict[Any, Dict[Any, List[Any]]] = {}
    for row in data:
        idx = row.get(index)
        col = row.get(columns)
        val = row.get(values)
        if idx not in raw:
            raw[idx] = {}
        if col not in raw[idx]:
            raw[idx][col] = []
        if val is not None:
            raw[idx][col].append(val)
    return {idx: {col: aggfunc(vals) for col, vals in cols.items()} for idx, cols in raw.items()}
