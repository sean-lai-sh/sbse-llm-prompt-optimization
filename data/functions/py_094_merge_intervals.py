from typing import List, Tuple


def merge_intervals(
    intervals: List[Tuple[int, int]],
    sort_first: bool = True
) -> List[Tuple[int, int]]:
    if not intervals:
        return []

    for start, end in intervals:
        if start > end:
            raise ValueError(f"Invalid interval ({start}, {end}): start > end")

    if sort_first:
        sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    else:
        sorted_intervals = list(intervals)

    merged: List[Tuple[int, int]] = [sorted_intervals[0]]

    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))

    return merged
