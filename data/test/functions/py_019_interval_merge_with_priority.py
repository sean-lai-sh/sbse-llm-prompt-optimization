from typing import List, Tuple


def interval_merge_with_priority(
    intervals: List[Tuple[int, int, int]],
) -> List[Tuple[int, int, int]]:
    """Merge overlapping (start, end, priority) intervals.

    When two intervals overlap, they are combined into one whose priority is
    the maximum of the merged segments. Ties keep the earlier priority.
    Input is not assumed to be sorted; output is sorted by start.
    """
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda iv: (iv[0], iv[1]))
    merged: List[Tuple[int, int, int]] = []
    cur_start, cur_end, cur_pri = sorted_intervals[0]
    for s, e, p in sorted_intervals[1:]:
        if s <= cur_end:
            cur_end = max(cur_end, e)
            cur_pri = max(cur_pri, p)
        else:
            merged.append((cur_start, cur_end, cur_pri))
            cur_start, cur_end, cur_pri = s, e, p
    merged.append((cur_start, cur_end, cur_pri))
    return merged
