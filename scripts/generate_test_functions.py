#!/usr/bin/env python3
"""Write the 50-function held-out test set to ``data/test/functions/``.

This script is purely deterministic — it writes a curated list of small,
self-contained source files (Python, JavaScript, TypeScript) that exercise
the same topic areas as the 500-function training set in ``data/functions/``
without overlapping function-name descriptors. It also emits the matching
``data/test/manifest.json`` describing language and complexity tier.

Reference summaries (``.txt`` files) are produced separately by
``scripts/generate_references.py`` invoked with the ``--functions-dir`` and
``--references-dir`` overrides pointing at this test set.

Usage:
    python scripts/generate_test_functions.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = REPO_ROOT / "data" / "test"
FUNCTIONS_DIR = TEST_DIR / "functions"
MANIFEST_PATH = TEST_DIR / "manifest.json"

LANGUAGE_BY_EXT = {".py": "python", ".js": "javascript", ".ts": "typescript"}


# Each entry: (filename, complexity_tier, source_code)
# Names below were checked against the 500-function training set to avoid
# descriptor collisions (see PR description for the full check).
FUNCTIONS: list[tuple[str, str, str]] = [
    # ---- Python: 20 functions (6 trivial / 10 medium / 4 complex) ----
    (
        "py_001_multiply_pair.py",
        "trivial",
        '''def multiply_pair(a: int, b: int) -> int:
    return a * b
''',
    ),
    (
        "py_002_is_negative.py",
        "trivial",
        '''def is_negative(n: float) -> bool:
    return n < 0
''',
    ),
    (
        "py_003_double_value.py",
        "trivial",
        '''def double_value(x: float) -> float:
    return x * 2
''',
    ),
    (
        "py_004_swap_pair.py",
        "trivial",
        '''from typing import Tuple


def swap_pair(a: int, b: int) -> Tuple[int, int]:
    return b, a
''',
    ),
    (
        "py_005_triangle_area.py",
        "trivial",
        '''def triangle_area(base: float, height: float) -> float:
    return 0.5 * base * height
''',
    ),
    (
        "py_006_circle_area.py",
        "trivial",
        '''import math


def circle_area(radius: float) -> float:
    if radius < 0:
        raise ValueError("radius must be non-negative")
    return math.pi * radius * radius
''',
    ),
    (
        "py_007_kth_smallest.py",
        "medium",
        '''from typing import List, Optional


def kth_smallest(arr: List[int], k: int) -> Optional[int]:
    if k < 1 or k > len(arr):
        return None
    pivot = arr[0]
    smaller = [x for x in arr[1:] if x < pivot]
    equal = [x for x in arr if x == pivot]
    larger = [x for x in arr[1:] if x > pivot]
    if k <= len(smaller):
        return kth_smallest(smaller, k)
    if k <= len(smaller) + len(equal):
        return pivot
    return kth_smallest(larger, k - len(smaller) - len(equal))
''',
    ),
    (
        "py_008_count_set_bits.py",
        "medium",
        '''def count_set_bits(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
''',
    ),
    (
        "py_009_decimal_to_binary.py",
        "medium",
        '''def decimal_to_binary(n: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    bits: list[str] = []
    while n:
        bits.append(str(n & 1))
        n >>= 1
    return sign + "".join(reversed(bits))
''',
    ),
    (
        "py_010_binary_to_decimal.py",
        "medium",
        '''def binary_to_decimal(bits: str) -> int:
    if not bits:
        raise ValueError("empty input")
    negative = False
    if bits.startswith("-"):
        negative = True
        bits = bits[1:]
    value = 0
    for ch in bits:
        if ch not in "01":
            raise ValueError(f"invalid bit: {ch!r}")
        value = (value << 1) | (1 if ch == "1" else 0)
    return -value if negative else value
''',
    ),
    (
        "py_011_running_total.py",
        "medium",
        '''from typing import List


def running_total(nums: List[float]) -> List[float]:
    out: List[float] = []
    total = 0.0
    for n in nums:
        total += n
        out.append(total)
    return out
''',
    ),
    (
        "py_012_find_missing_number.py",
        "medium",
        '''from typing import List


def find_missing_number(nums: List[int]) -> int:
    """Given a list containing n distinct numbers in [0, n], return the missing one."""
    n = len(nums)
    expected = n * (n + 1) // 2
    actual = sum(nums)
    return expected - actual
''',
    ),
    (
        "py_013_valid_parentheses_pairs.py",
        "medium",
        '''def valid_parentheses_pairs(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''',
    ),
    (
        "py_014_find_peak_element.py",
        "medium",
        '''from typing import List


def find_peak_element(nums: List[int]) -> int:
    """Return any index i such that nums[i] > nums[i-1] and nums[i] > nums[i+1].

    Out-of-bounds neighbours are treated as -infinity. Uses binary search in O(log n).
    """
    if not nums:
        raise ValueError("empty input")
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[mid + 1]:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    ),
    (
        "py_015_levenshtein_iterative.py",
        "medium",
        '''def levenshtein_iterative(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr[j] = min(
                curr[j - 1] + 1,        # insertion
                prev[j] + 1,            # deletion
                prev[j - 1] + cost,     # substitution
            )
        prev = curr
    return prev[-1]
''',
    ),
    (
        "py_016_roman_numeral_add.py",
        "medium",
        '''def roman_numeral_add(a: str, b: str) -> str:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    def to_int(s: str) -> int:
        total = 0
        prev = 0
        for ch in reversed(s.upper()):
            v = values[ch]
            total += -v if v < prev else v
            prev = v
        return total

    def to_roman(n: int) -> str:
        symbols = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ]
        out = []
        for value, sym in symbols:
            while n >= value:
                out.append(sym)
                n -= value
        return "".join(out)

    return to_roman(to_int(a) + to_int(b))
''',
    ),
    (
        "py_017_bfs_shortest_path.py",
        "complex",
        '''from collections import deque
from typing import Dict, List, Optional


def bfs_shortest_path(graph: Dict[int, List[int]], src: int, dst: int) -> Optional[List[int]]:
    """Return the shortest path (by edge count) from src to dst in an unweighted graph.

    Returns None if dst is unreachable. The path includes both endpoints.
    """
    if src == dst:
        return [src]
    if src not in graph:
        return None
    visited = {src}
    parent: Dict[int, int] = {}
    queue: deque[int] = deque([src])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = node
            if nxt == dst:
                path = [dst]
                cur = dst
                while cur in parent:
                    cur = parent[cur]
                    path.append(cur)
                return list(reversed(path))
            queue.append(nxt)
    return None
''',
    ),
    (
        "py_018_topological_sort_kahn.py",
        "complex",
        '''from collections import deque
from typing import Dict, List, Optional


def topological_sort_kahn(graph: Dict[int, List[int]]) -> Optional[List[int]]:
    """Kahn's algorithm. Returns a topological ordering of the DAG, or None if a cycle exists."""
    indeg: Dict[int, int] = {node: 0 for node in graph}
    for node, succs in graph.items():
        for s in succs:
            indeg[s] = indeg.get(s, 0) + 1
            indeg.setdefault(node, 0)
    queue: deque[int] = deque(sorted(n for n, d in indeg.items() if d == 0))
    order: List[int] = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for s in graph.get(n, []):
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    if len(order) != len(indeg):
        return None
    return order
''',
    ),
    (
        "py_019_interval_merge_with_priority.py",
        "complex",
        '''from typing import List, Tuple


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
''',
    ),
    (
        "py_020_regex_match_dotstar.py",
        "complex",
        '''def regex_match_dotstar(text: str, pattern: str) -> bool:
    """Check whether ``pattern`` matches the entirety of ``text``.

    The pattern dialect supports literal characters, ``.`` (any single character),
    and ``*`` (zero-or-more of the preceding element). Implemented with a 2D DP
    table in O(len(text) * len(pattern)) time.
    """
    m, n = len(text), len(pattern)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if pattern[j - 1] == "*" and j >= 2:
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            pc = pattern[j - 1]
            if pc == "*":
                dp[i][j] = dp[i][j - 2]
                prev = pattern[j - 2]
                if prev == "." or prev == text[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            else:
                if pc == "." or pc == text[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]
''',
    ),
    # ---- JavaScript: 15 functions (5 trivial / 7 medium / 3 complex) ----
    (
        "js_001_negate.js",
        "trivial",
        '''export default function negate(x) {
  return -x;
}
''',
    ),
    (
        "js_002_isPositive.js",
        "trivial",
        '''export default function isPositive(n) {
  return n > 0;
}
''',
    ),
    (
        "js_003_halve.js",
        "trivial",
        '''export default function halve(x) {
  return x / 2;
}
''',
    ),
    (
        "js_004_subtractArray.js",
        "trivial",
        '''export default function subtractArray(arr) {
  if (arr.length === 0) return 0;
  return arr.slice(1).reduce((acc, n) => acc - n, arr[0]);
}
''',
    ),
    (
        "js_005_productArray.js",
        "trivial",
        '''export default function productArray(arr) {
  return arr.reduce((p, n) => p * n, 1);
}
''',
    ),
    (
        "js_006_mapValues.js",
        "medium",
        '''export default function mapValues(obj, fn) {
  const out = {};
  for (const key of Object.keys(obj)) {
    out[key] = fn(obj[key], key);
  }
  return out;
}
''',
    ),
    (
        "js_007_filterDuplicates.js",
        "medium",
        '''export default function filterDuplicates(arr) {
  const counts = new Map();
  for (const item of arr) {
    counts.set(item, (counts.get(item) || 0) + 1);
  }
  return arr.filter((item) => counts.get(item) === 1);
}
''',
    ),
    (
        "js_008_partitionArray.js",
        "medium",
        '''export default function partitionArray(arr, predicate) {
  const truthy = [];
  const falsy = [];
  for (const item of arr) {
    if (predicate(item)) truthy.push(item);
    else falsy.push(item);
  }
  return [truthy, falsy];
}
''',
    ),
    (
        "js_009_binarySearchFirst.js",
        "medium",
        '''export default function binarySearchFirst(arr, target) {
  let lo = 0;
  let hi = arr.length - 1;
  let result = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >>> 1;
    if (arr[mid] === target) {
      result = mid;
      hi = mid - 1;
    } else if (arr[mid] < target) {
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return result;
}
''',
    ),
    (
        "js_010_runLengthDecode.js",
        "medium",
        '''export default function runLengthDecode(encoded) {
  let out = "";
  let i = 0;
  while (i < encoded.length) {
    let j = i;
    while (j < encoded.length && /\\d/.test(encoded[j])) j += 1;
    if (j === i) throw new Error(`expected count at position ${i}`);
    const count = Number(encoded.slice(i, j));
    if (j >= encoded.length) throw new Error("dangling count without character");
    out += encoded[j].repeat(count);
    i = j + 1;
  }
  return out;
}
''',
    ),
    (
        "js_011_levenshteinDistance.js",
        "medium",
        '''export default function levenshteinDistance(a, b) {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i += 1) {
    const curr = [i];
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      curr[j] = Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
    }
    prev = curr;
  }
  return prev[b.length];
}
''',
    ),
    (
        "js_012_singleNumberXor.js",
        "medium",
        '''export default function singleNumberXor(nums) {
  let acc = 0;
  for (const n of nums) {
    acc ^= n;
  }
  return acc;
}
''',
    ),
    (
        "js_013_intervalSchedulingMaximizer.js",
        "complex",
        '''export default function intervalSchedulingMaximizer(intervals) {
  if (!intervals.length) return [];
  const sorted = [...intervals].sort((a, b) => a[1] - b[1]);
  const chosen = [sorted[0]];
  let lastEnd = sorted[0][1];
  for (let i = 1; i < sorted.length; i += 1) {
    const [start, end] = sorted[i];
    if (start >= lastEnd) {
      chosen.push(sorted[i]);
      lastEnd = end;
    }
  }
  return chosen;
}
''',
    ),
    (
        "js_014_wordLadderBfs.js",
        "complex",
        '''export default function wordLadderBfs(begin, end, wordList) {
  const dict = new Set(wordList);
  if (!dict.has(end)) return 0;
  let frontier = new Set([begin]);
  const visited = new Set([begin]);
  let steps = 1;
  while (frontier.size > 0) {
    const next = new Set();
    for (const word of frontier) {
      if (word === end) return steps;
      const chars = word.split("");
      for (let i = 0; i < chars.length; i += 1) {
        const original = chars[i];
        for (let c = 97; c <= 122; c += 1) {
          const candidate = String.fromCharCode(c);
          if (candidate === original) continue;
          chars[i] = candidate;
          const swapped = chars.join("");
          if (dict.has(swapped) && !visited.has(swapped)) {
            visited.add(swapped);
            next.add(swapped);
          }
        }
        chars[i] = original;
      }
    }
    frontier = next;
    steps += 1;
  }
  return 0;
}
''',
    ),
    (
        "js_015_tarjanSCC.js",
        "complex",
        '''export default function tarjanSCC(graph) {
  const index = new Map();
  const lowlink = new Map();
  const onStack = new Set();
  const stack = [];
  const result = [];
  let counter = 0;

  const strongconnect = (v) => {
    index.set(v, counter);
    lowlink.set(v, counter);
    counter += 1;
    stack.push(v);
    onStack.add(v);
    for (const w of graph[v] || []) {
      if (!index.has(w)) {
        strongconnect(w);
        lowlink.set(v, Math.min(lowlink.get(v), lowlink.get(w)));
      } else if (onStack.has(w)) {
        lowlink.set(v, Math.min(lowlink.get(v), index.get(w)));
      }
    }
    if (lowlink.get(v) === index.get(v)) {
      const component = [];
      let w;
      do {
        w = stack.pop();
        onStack.delete(w);
        component.push(w);
      } while (w !== v);
      result.push(component);
    }
  };

  for (const node of Object.keys(graph)) {
    if (!index.has(node)) strongconnect(node);
  }
  return result;
}
''',
    ),
    # ---- TypeScript: 15 functions (4 trivial / 8 medium / 3 complex) ----
    (
        "ts_001_multiplyBy.ts",
        "trivial",
        '''export function multiplyBy(x: number, factor: number): number {
  return x * factor;
}
''',
    ),
    (
        "ts_002_floorDiv.ts",
        "trivial",
        '''export function floorDiv(a: number, b: number): number {
  if (b === 0) throw new Error("division by zero");
  return Math.floor(a / b);
}
''',
    ),
    (
        "ts_003_mod.ts",
        "trivial",
        '''export function mod(a: number, b: number): number {
  if (b === 0) throw new Error("modulo by zero");
  return ((a % b) + b) % b;
}
''',
    ),
    (
        "ts_004_parityFlag.ts",
        "trivial",
        '''export function parityFlag(n: number): "even" | "odd" {
  return n % 2 === 0 ? "even" : "odd";
}
''',
    ),
    (
        "ts_005_partitionByPivot.ts",
        "medium",
        '''export function partitionByPivot(arr: number[], pivot: number): number[] {
  const less: number[] = [];
  const equal: number[] = [];
  const greater: number[] = [];
  for (const n of arr) {
    if (n < pivot) less.push(n);
    else if (n === pivot) equal.push(n);
    else greater.push(n);
  }
  return [...less, ...equal, ...greater];
}
''',
    ),
    (
        "ts_006_coinSumWays.ts",
        "medium",
        '''export function coinSumWays(amount: number, coins: number[]): number {
  if (amount < 0) return 0;
  const dp = new Array<number>(amount + 1).fill(0);
  dp[0] = 1;
  for (const coin of coins) {
    for (let a = coin; a <= amount; a += 1) {
      dp[a] += dp[a - coin];
    }
  }
  return dp[amount];
}
''',
    ),
    (
        "ts_007_findFirstUnique.ts",
        "medium",
        '''export function findFirstUnique<T>(arr: T[]): T | undefined {
  const counts = new Map<T, number>();
  for (const item of arr) {
    counts.set(item, (counts.get(item) ?? 0) + 1);
  }
  for (const item of arr) {
    if (counts.get(item) === 1) return item;
  }
  return undefined;
}
''',
    ),
    (
        "ts_008_removeDuplicatesSortedArray.ts",
        "medium",
        '''export function removeDuplicatesSortedArray(arr: number[]): number {
  if (arr.length === 0) return 0;
  let write = 1;
  for (let read = 1; read < arr.length; read += 1) {
    if (arr[read] !== arr[write - 1]) {
      arr[write] = arr[read];
      write += 1;
    }
  }
  arr.length = write;
  return write;
}
''',
    ),
    (
        "ts_009_validBracketsTyped.ts",
        "medium",
        '''export function validBracketsTyped(s: string): boolean {
  const pairs: Record<string, string> = { ")": "(", "]": "[", "}": "{" };
  const stack: string[] = [];
  for (const ch of s) {
    if (ch === "(" || ch === "[" || ch === "{") {
      stack.push(ch);
    } else if (ch in pairs) {
      if (stack.pop() !== pairs[ch]) return false;
    }
  }
  return stack.length === 0;
}
''',
    ),
    (
        "ts_010_levenshteinTyped.ts",
        "medium",
        '''export function levenshteinTyped(a: string, b: string): number {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  let prev: number[] = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i += 1) {
    const curr: number[] = [i];
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      curr.push(Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost));
    }
    prev = curr;
  }
  return prev[b.length];
}
''',
    ),
    (
        "ts_011_nthFibonacciIter.ts",
        "medium",
        '''export function nthFibonacciIter(n: number): number {
  if (n < 0) throw new Error("n must be non-negative");
  if (n < 2) return n;
  let a = 0;
  let b = 1;
  for (let i = 2; i <= n; i += 1) {
    const next = a + b;
    a = b;
    b = next;
  }
  return b;
}
''',
    ),
    (
        "ts_012_groupAnagramsTyped.ts",
        "medium",
        '''export function groupAnagramsTyped(words: string[]): string[][] {
  const buckets = new Map<string, string[]>();
  for (const word of words) {
    const key = word.split("").sort().join("");
    const list = buckets.get(key);
    if (list) list.push(word);
    else buckets.set(key, [word]);
  }
  return Array.from(buckets.values());
}
''',
    ),
    (
        "ts_013_kmpFailureTable.ts",
        "complex",
        '''export function kmpFailureTable(pattern: string): number[] {
  const table = new Array<number>(pattern.length).fill(0);
  let len = 0;
  let i = 1;
  while (i < pattern.length) {
    if (pattern[i] === pattern[len]) {
      len += 1;
      table[i] = len;
      i += 1;
    } else if (len !== 0) {
      len = table[len - 1];
    } else {
      table[i] = 0;
      i += 1;
    }
  }
  return table;
}
''',
    ),
    (
        "ts_014_dijkstraTyped.ts",
        "complex",
        '''type Edge = { to: number; weight: number };

export function dijkstraTyped(graph: Map<number, Edge[]>, source: number): Map<number, number> {
  const dist = new Map<number, number>();
  for (const node of graph.keys()) dist.set(node, Number.POSITIVE_INFINITY);
  dist.set(source, 0);

  const visited = new Set<number>();
  const pending = new Set<number>(graph.keys());
  while (pending.size > 0) {
    let current: number | null = null;
    let currentDist = Number.POSITIVE_INFINITY;
    for (const node of pending) {
      const d = dist.get(node) ?? Number.POSITIVE_INFINITY;
      if (d < currentDist) {
        currentDist = d;
        current = node;
      }
    }
    if (current === null || currentDist === Number.POSITIVE_INFINITY) break;
    pending.delete(current);
    visited.add(current);
    for (const edge of graph.get(current) ?? []) {
      if (visited.has(edge.to)) continue;
      const alt = currentDist + edge.weight;
      if (alt < (dist.get(edge.to) ?? Number.POSITIVE_INFINITY)) {
        dist.set(edge.to, alt);
      }
    }
  }
  return dist;
}
''',
    ),
    (
        "ts_015_editDistanceDP.ts",
        "complex",
        '''export function editDistanceDP(
  source: string,
  target: string,
  insertCost = 1,
  deleteCost = 1,
  replaceCost = 1,
): number {
  const m = source.length;
  const n = target.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array<number>(n + 1).fill(0));
  for (let i = 0; i <= m; i += 1) dp[i][0] = i * deleteCost;
  for (let j = 0; j <= n; j += 1) dp[0][j] = j * insertCost;
  for (let i = 1; i <= m; i += 1) {
    for (let j = 1; j <= n; j += 1) {
      if (source[i - 1] === target[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + deleteCost,
          dp[i][j - 1] + insertCost,
          dp[i - 1][j - 1] + replaceCost,
        );
      }
    }
  }
  return dp[m][n];
}
''',
    ),
]


def language_for(filename: str) -> str:
    suffix = Path(filename).suffix
    return LANGUAGE_BY_EXT[suffix]


def main() -> int:
    FUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)

    if len(FUNCTIONS) != 50:
        raise SystemExit(f"expected 50 functions, got {len(FUNCTIONS)}")

    manifest: list[dict[str, str]] = []
    for filename, tier, source in FUNCTIONS:
        out_path = FUNCTIONS_DIR / filename
        out_path.write_text(source, encoding="utf-8")
        manifest.append(
            {
                "filename": filename,
                "language": language_for(filename),
                "complexity_tier": tier,
            }
        )
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(manifest)} functions to {FUNCTIONS_DIR}")
    print(f"Wrote manifest to {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
