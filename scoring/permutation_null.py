#!/usr/bin/env python3
"""The permutation null, its seed discipline, and its multiplicity correction.

Written as a module rather than inline in the scorer so the procedure is CITABLE
and so a second engine's p-values are produced by the same machinery as the
first's. Nothing here reads a log, knows what FinMem is, or has an opinion about
what counts as a finding.

Until 2026-08-09 this existed as three loops inside `score_pilot.py` with
`NULL_DRAWS = 2_000`, seeds spelled `RNG_SEED + 1 / +2 / +3`, and no multiplicity
correction of any kind against a grid that will be 20 items x 3 classes = 60
tests. All three are fixed below.


THE NULL
--------
Question: how often does the SAME text produce a divergence this large, by chance
alone?

The control JSD (BASE vs FLOOR) answers a weaker question -- it is ONE realization
of same-input noise, and one realization cannot say whether an observed divergence
is unusual. So the pooled same-input draws (FLOOR and BASE are the same text run
as two separate blocks) are resampled into two independent samples of the OBSERVED
sizes, and the null is the distribution of their divergence.

Two properties that are not incidental:

- SIZES ARE RESPECTED. JSD between two small samples is larger on average than
  between two large ones, purely from sampling. A 20-draw variant scored against a
  null built from 50-draw groups would understate the noise and manufacture
  significance.
- WITH REPLACEMENT rather than a strict permutation, because a class can have more
  runs than the same-input pool has draws -- three N1 variants at 20 reps is 60
  against a pool of 50. "Permutation null" is kept as the name because that is
  what it is called; the resampling scheme is stated here so the name does not
  have to carry it.

`(hits + 1) / (draws + 1)` in both places: a p-value of exactly 0 is not something
a finite resample can justify, and reporting one invites a reader to believe it.
The floor is therefore 1/(draws+1) -- at the default 10,000 that is 0.0001, where
the previous 2,000 floored at 0.0005 and the smallest observed p had already been
reported as 0.000.


SEED DISCIPLINE
---------------
ONE root seed. Every stream is derived from it BY NAME through a SeedSequence, so:

- a report is reproducible from the logs and the root seed alone;
- adding a fourth analysis cannot shift the streams of the first three, which
  `RNG_SEED + 1 / +2 / +3` could not promise -- inserting an analysis in the
  middle renumbered everything after it and silently changed published intervals;
- two analyses can never collide on the same stream by arithmetic accident.

The name is hashed with blake2b rather than `hash()`, which is randomized per
process for strings and would make the derivation irreproducible across runs.


MULTIPLICITY
------------
The family is the whole item x class grid, corrected in one pass -- not per class,
which would treat three 20-test screens as three independent questions and correct
each too gently.

Both corrections are reported beside the raw p, by decision of the project lead
(2026-08-09):

- BENJAMINI-HOCHBERG controls the false discovery rate. It suits the question the
  grid actually asks -- WHICH items moved -- where a fixed share of false positives
  among the flagged cells is an acceptable price for power.
- HOLM controls the family-wise error rate. It is the one to read if any single
  cell would be quoted on its own, because then one false positive anywhere is one
  false claim.

Raw values are never dropped. A cell whose p is undefined (no variant runs, an
empty pool) is excluded from the family and COUNTED, because m is the number of
tests actually performed and a silent exclusion would shrink every adjusted p.
"""

from __future__ import annotations

import hashlib
from typing import Dict, Hashable, List, Tuple

import numpy as np

from divergence import distribution, jensen_shannon

# Final-run default. A CLI flag lowers it for iteration; the value used is printed
# in the report, so a fast run cannot be mistaken for a final one.
NULL_DRAWS_DEFAULT = 10_000


def derive_rng(root_seed: int, stream: str) -> np.random.Generator:
    """An independent generator for a NAMED analysis, derived from the root seed.

    Deterministic across processes and platforms: blake2b of the name, not
    `hash()`, which numpy would accept and which is salted per process.
    """
    tag = int.from_bytes(hashlib.blake2b(stream.encode("utf-8"), digest_size=8).digest(), "big")
    return np.random.default_rng(np.random.SeedSequence([root_seed, tag]))


def null_pvalue(
    pool: List[str],
    n_variant: int,
    n_base: int,
    observed: float,
    rng: np.random.Generator,
    draws: int = NULL_DRAWS_DEFAULT,
) -> float:
    """Share of same-input resamples reaching `observed`. See THE NULL above."""
    if not pool or observed != observed:  # empty, or NaN
        return float("nan")
    arr = np.array(pool)
    hits = 0
    for _ in range(draws):
        a = rng.choice(arr, size=n_variant, replace=True)
        b = rng.choice(arr, size=n_base, replace=True)
        if jensen_shannon(distribution(list(a)), distribution(list(b))) >= observed:
            hits += 1
    return (hits + 1) / (draws + 1)


def benjamini_hochberg(pvalues: List[float]) -> List[float]:
    """BH-adjusted p, monotonicity enforced from the largest downward."""
    m = len(pvalues)
    if m == 0:
        return []
    order = np.argsort(pvalues)
    adjusted = [0.0] * m
    running = 1.0
    for rank in range(m, 0, -1):
        idx = int(order[rank - 1])
        running = min(running, pvalues[idx] * m / rank)
        adjusted[idx] = min(1.0, running)
    return adjusted


def holm(pvalues: List[float]) -> List[float]:
    """Holm-adjusted p, monotonicity enforced from the smallest upward."""
    m = len(pvalues)
    if m == 0:
        return []
    order = np.argsort(pvalues)
    adjusted = [0.0] * m
    running = 0.0
    for rank in range(1, m + 1):
        idx = int(order[rank - 1])
        running = max(running, pvalues[idx] * (m - rank + 1))
        adjusted[idx] = min(1.0, running)
    return adjusted


def adjust_family(
    pvalues: Dict[Hashable, float],
) -> Tuple[Dict[Hashable, Dict[str, float]], int, List[Hashable]]:
    """Correct one family of tests. Returns (per-cell raw/bh/holm, m, undefined keys).

    `m` is the number of tests actually performed, which is what the correction
    must divide by; cells with an undefined p are named back to the caller so the
    report can count them rather than lose them.
    """
    defined = [k for k, v in pvalues.items() if v == v]
    undefined = [k for k in pvalues if k not in set(defined)]
    raw = [pvalues[k] for k in defined]
    bh = benjamini_hochberg(raw)
    hm = holm(raw)
    out: Dict[Hashable, Dict[str, float]] = {
        key: {"raw": raw[i], "bh": bh[i], "holm": hm[i]} for i, key in enumerate(defined)
    }
    for key in undefined:
        out[key] = {"raw": float("nan"), "bh": float("nan"), "holm": float("nan")}
    return out, len(defined), undefined
