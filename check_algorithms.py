"""
check_algorithms.py
--------------------
Manual verification script for TaskFlow's custom algorithms.
No pytest / unittest required — plain if/else with PASS/FAIL prints.

Run with:
    python check_algorithms.py
"""

from backend.algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)

results = []


def check(name: str, condition: bool):
    if condition:
        print(f"PASS: {name}")
        results.append(True)
    else:
        print(f"FAIL: {name}")
        results.append(False)


# --------------------------------------------------- Empty insertion sort
data = []
insertion_sort(data, key=lambda x: x["v"])
check("Empty insertion sort", data == [])

# ------------------------------------------------------------ Single element
data = [{"v": 5}]
insertion_sort(data, key=lambda x: x["v"])
check("Single element", data == [{"v": 5}])

# ------------------------------------------------------------- Basic sort
data = [{"v": 3}, {"v": 1}, {"v": 2}]
insertion_sort(data, key=lambda x: x["v"])
check("Insertion sort basic order", [d["v"] for d in data] == [1, 2, 3])

# --------------------------------------------------------- Binary search
sorted_data = [{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}, {"v": 5}]
check("Binary search first", binary_search(sorted_data, 1, key=lambda x: x["v"]) == 0)
check("Binary search middle", binary_search(sorted_data, 3, key=lambda x: x["v"]) == 2)
check("Binary search last", binary_search(sorted_data, 5, key=lambda x: x["v"]) == 4)
check("Binary search absent", binary_search(sorted_data, 99, key=lambda x: x["v"]) == -1)

# --------------------------------------------------------- Linear search
unsorted_data = [{"v": 4}, {"v": 2}, {"v": 9}, {"v": 1}]
check("Linear search found", linear_search(unsorted_data, 9, key=lambda x: x["v"]) == 2)
check("Linear search absent", linear_search(unsorted_data, 100, key=lambda x: x["v"]) == -1)

# ----------------------------------------------------------- Count variants
count_data = [{"v": 5}, {"v": 3}, {"v": 4}, {"v": 1}, {"v": 2}]
_, comparisons = insertion_sort_count(count_data, key=lambda x: x["v"])
check("Insertion sort count", comparisons > 0 and [d["v"] for d in count_data] == [1, 2, 3, 4, 5])

sorted_count_data = [{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}, {"v": 5}]
idx, comparisons = binary_search_count(sorted_count_data, 4, key=lambda x: x["v"])
check("Binary search count", idx == 3 and comparisons > 0)

idx, comparisons = linear_search_count(sorted_count_data, 4, key=lambda x: x["v"])
check("Linear search count", idx == 3 and comparisons == 4)

# ---------------------------------------------------------------- Summary
total = len(results)
passed = sum(results)
print(f"\n{passed}/{total} checks passed.")
if passed != total:
    raise SystemExit(1)
