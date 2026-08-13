"""
def insertion_sort(    # Ascending order sort; comparisons happen strictly on the provided key.)
algorithms.py
-------------
Custom DSA implementations used by TaskFlow. These are used directly by
the /tasks (sort) and /tasks/search endpoints — no built-in sorted(),
list.sort(), or third-party search is used anywhere in this module.

Not-found convention: every search function returns -1 when the target
value is not present, matching classic array-search convention rather
than raising an exception. Callers translate -1 into an HTTP 404.
"""

from typing import Any, Callable, List, Tuple


def insertion_sort(records: List[dict], key: Callable[[dict], Any]) -> List[dict]:
    """
    Classic insertion sort, mutated in place, ascending order.

    Starts from the second element (index 1), compares it against the
    already-sorted prefix to its left, shifting larger elements one
    slot to the right until the correct insertion point is found.

    Returns the same list object for convenience (records is mutated).
    """
    for i in range(1, len(records)):
        current = records[i]
        current_key = key(current)
        j = i - 1
        while j >= 0 and key(records[j]) > current_key:
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = current
    return records


def binary_search(
    sorted_records: List[dict], target_value: Any, key: Callable[[dict], Any]
) -> int:
    """
    Iterative binary search over a list already sorted ascending by `key`.

    Returns the index of the first match found, or -1 if the target
    value is not present. Because binary search does not guarantee
    finding the first occurrence among duplicates, "index of *a*
    match" is the documented not-found/found contract here.
    """
    low, high = 0, len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_value = key(sorted_records[mid])
        if mid_value == target_value:
            return mid
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def linear_search(
    records: List[dict], target_value: Any, key: Callable[[dict], Any]
) -> int:
    """
    Sequential scan. Returns the index of the first matching element,
    or -1 if no element matches.
    """
    for i, record in enumerate(records):
        if key(record) == target_value:
            return i
    return -1


# --------------------------------------------------------- Benchmarking --
def insertion_sort_count(records: List[dict], key: Callable[[dict], Any]) -> Tuple[List[dict], int]:
    """Same algorithm as insertion_sort, but also returns the number of
    key comparisons performed, for benchmarking purposes."""
    comparisons = 0
    for i in range(1, len(records)):
        current = records[i]
        current_key = key(current)
        j = i - 1
        while j >= 0:
            comparisons += 1
            if key(records[j]) > current_key:
                records[j + 1] = records[j]
                j -= 1
            else:
                break
        records[j + 1] = current
    return records, comparisons


def binary_search_count(
    sorted_records: List[dict], target_value: Any, key: Callable[[dict], Any]
) -> Tuple[int, int]:
    """Same algorithm as binary_search, but also returns the number of
    comparisons performed."""
    comparisons = 0
    low, high = 0, len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_value = key(sorted_records[mid])
        if mid_value == target_value:
            return mid, comparisons
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1, comparisons


def linear_search_count(
    records: List[dict], target_value: Any, key: Callable[[dict], Any]
) -> Tuple[int, int]:
    """Same algorithm as linear_search, but also returns the number of
    comparisons performed."""
    comparisons = 0
    for i, record in enumerate(records):
        comparisons += 1
        if key(record) == target_value:
            return i, comparisons
    return -1, comparisons
