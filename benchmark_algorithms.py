"""
benchmark_algorithms.py
------------------------
Benchmarks insertion_sort_count, binary_search_count, and
linear_search_count against realistic TaskFlow-shaped records at
10 / 500 / 3000 records. Prints raw comparison counts and saves
results to benchmark_results.txt.

Run with:
    python benchmark_algorithms.py
"""

import random
import copy

from backend.algorithms import (
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)

PRIORITIES = ["low", "medium", "high"]
PRIORITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}


def make_records(n: int) -> list[dict]:
    random.seed(42)
    return [
        {
            "id": i,
            "title": f"Task-{random.randint(0, n * 10)}",
            "priority": random.choice(PRIORITIES),
        }
        for i in range(n)
    ]


def run_benchmark(n: int) -> str:
    records = make_records(n)

    # Insertion sort by priority weight.
    sort_input = copy.deepcopy(records)
    _, sort_comparisons = insertion_sort_count(
        sort_input, key=lambda r: PRIORITY_WEIGHT[r["priority"]]
    )

    # Binary search needs a title-sorted index.
    title_index = copy.deepcopy(records)
    title_index, _ = insertion_sort_count(title_index, key=lambda r: r["title"])
    target_title = title_index[len(title_index) // 2]["title"] if title_index else None
    _, binary_comparisons = binary_search_count(
        title_index, target_title, key=lambda r: r["title"]
    )

    # Linear search over the unsorted records.
    _, linear_comparisons = linear_search_count(
        records, target_title, key=lambda r: r["title"]
    )

    return (
        f"n={n:>5} | insertion_sort comparisons={sort_comparisons:>8} | "
        f"binary_search comparisons={binary_comparisons:>4} | "
        f"linear_search comparisons={linear_comparisons:>6}"
    )


def main():
    lines = ["TaskFlow Algorithm Benchmark Results", "=" * 60]
    for n in (10, 500, 3000):
        line = run_benchmark(n)
        print(line)
        lines.append(line)

    with open("benchmark_results.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\nResults saved to benchmark_results.txt")


if __name__ == "__main__":
    main()
