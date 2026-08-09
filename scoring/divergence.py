#!/usr/bin/env python3
"""Distributional primitives, shared by the scorer and the permutation null.

Extracted for one reason and no other: `permutation_null` has to compute the SAME
divergence the scorer reports -- a null built from a different statistic than the
observed value is not a null of anything -- and importing it back out of
`score_pilot` would be circular.

There is no policy in this file. Three pure functions over a list of action
strings, no seeds, no thresholds, no logs.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List

import numpy as np


def distribution(actions: List[str]) -> Dict[str, float]:
    """Action shares. An empty list is an empty distribution, not a uniform one."""
    counts = Counter(actions)
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total else {}


def disagreement(actions: List[str]) -> float:
    """1 - sum(p^2): the chance two independent draws disagree.

    This is the probability that two runs of the SAME input differ, which is
    exactly what a flip rate must be compared against.
    """
    if len(actions) < 2:
        return float("nan")
    counts = Counter(actions)
    total = sum(counts.values())
    return 1.0 - sum((n / total) ** 2 for n in counts.values())


def jensen_shannon(p: Dict[str, float], q: Dict[str, float]) -> float:
    """JSD in bits, so 0 means identical and 1 means disjoint support."""
    keys = sorted(set(p) | set(q))
    pv = np.array([p.get(k, 0.0) for k in keys], dtype=float)
    qv = np.array([q.get(k, 0.0) for k in keys], dtype=float)
    pv = pv / pv.sum() if pv.sum() else pv
    qv = qv / qv.sum() if qv.sum() else qv
    m = 0.5 * (pv + qv)

    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))

    return 0.5 * kl(pv, m) + 0.5 * kl(qv, m)
