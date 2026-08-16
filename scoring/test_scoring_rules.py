#!/usr/bin/env python3
"""Pins the three pre-registered scoring rules (gaps-list item 2).

These are not style tests. The rules were fixed by the project lead on 2026-08-09
BEFORE any real fixture existed, and they are shared with every future engine so
two engines' figures are comparable -- so a change to any constant or procedure
below changes what the study measured, and has to be a deliberate act with a new
registration rather than an edit that still passes.

The rehearsal is what each rule is pinned against, because the rehearsal is where
each one failed. Runs under pytest or as a plain script, from the repo root:

    docker run --rm -e FP_REQUIRE_KEYS=0 -v <repo>:/work \\
      -w /work <any-arm-image> python -m pytest scoring/test_scoring_rules.py -q

No API calls, no logs written; the one end-to-end tie case finds its rehearsal
log by GLOB over the arms -- scoring may not assume any arm's layout beyond
"arms hold their runs somewhere below arms/" -- and skips itself, by returning,
when no arm carries it. Everything else is pure and runs anywhere.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import divergence as dv  # noqa: E402
import permutation_null as pn  # noqa: E402
import score_pilot as sp  # noqa: E402

# The monorepo root; the arms live under it.
ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# RULE 1 -- a tied baseline is excluded from flip-rate scoring
# --------------------------------------------------------------------------

def test_exact_tie_has_no_baseline():
    """The rehearsal's S01 shape. `Counter.most_common` answered this `buy`."""
    result = sp.baseline_of(["buy", "buy", "hold", "sell", "sell"])
    assert result["action"] is None
    assert result["tied"] == ["buy", "sell"]
    assert result["margin"] == 0.0


def test_tie_detection_is_order_independent():
    """The bug being fixed WAS insertion order, so the fix must not depend on it."""
    a = sp.baseline_of(["buy", "buy", "hold", "sell", "sell"])
    b = sp.baseline_of(["sell", "sell", "hold", "buy", "buy"])
    assert a["action"] is b["action"] is None
    assert a["tied"] == b["tied"]


def test_clear_baseline_survives():
    result = sp.baseline_of(["buy", "buy", "buy", "hold", "sell"])
    assert result["action"] == "buy"
    assert abs(result["margin"] - 0.4) < 1e-12


def test_margin_exposes_a_near_tie():
    """9-vs-8 is not a tie and is barely less arbitrary. Reported, not acted on."""
    result = sp.baseline_of(["buy"] * 9 + ["sell"] * 8)
    assert result["action"] == "buy"
    assert 0.0 < result["margin"] < 0.06


def test_unanimous_baseline_has_full_margin():
    result = sp.baseline_of(["hold"] * 20)
    assert result["action"] == "hold" and result["margin"] == 1.0


# --------------------------------------------------------------------------
# RULE 2 -- flip rate carries an interpretability verdict; JSD governs always
# --------------------------------------------------------------------------

def test_registered_threshold_is_unchanged():
    """Changing this changes what every reported flip rate means."""
    assert sp.PHI_INTERPRETABLE_MAX == 0.20


def test_gate_passes_only_a_low_floor():
    assert sp.flip_verdict("S01", 0.064, 0.20, tied=False) is None


def test_gate_is_strict_at_the_boundary():
    """phi < threshold, not <=. A registered constant should not need a footnote."""
    assert sp.flip_verdict("X", 0.20, 0.20, tied=False) is not None


def test_gate_states_its_reason():
    """The report prints the reason IN PLACE OF the number, so the reason is data."""
    assert "phi = 0.638" in sp.flip_verdict("S03", 0.6378, 0.20, tied=False)
    assert "tied baseline" in sp.flip_verdict("S01", 0.05, 0.20, tied=True)
    assert "no floor" in sp.flip_verdict("X", float("nan"), 0.20, tied=False)


def test_tie_beats_a_passing_floor():
    """A tie disqualifies regardless of phi -- the two failures are independent."""
    assert sp.flip_verdict("X", 0.01, 0.20, tied=True) is not None


# --------------------------------------------------------------------------
# RULE 3 -- the null, its seeds, and its multiplicity correction
# --------------------------------------------------------------------------

def test_final_run_draw_count():
    """2,000 floored p at 0.0005 while a p of 0.000 was already being reported."""
    assert pn.NULL_DRAWS_DEFAULT == 10_000


def test_pvalue_floor_is_one_over_draws_plus_one():
    rng = pn.derive_rng(1, "t")
    pool = ["buy"] * 10 + ["sell"] * 10
    assert abs(pn.null_pvalue(pool, 10, 10, 99.0, rng, draws=200) - 1 / 201) < 1e-12
    assert abs(pn.null_pvalue(pool, 10, 10, -1.0, rng, draws=200) - 1.0) < 1e-12


def test_undefined_pvalue_is_nan_not_zero():
    rng = pn.derive_rng(1, "t")
    value = pn.null_pvalue([], 1, 1, 0.1, rng, draws=10)
    assert value != value


def test_named_streams_are_reproducible_and_distinct():
    """The whole point of dropping `RNG_SEED + 1 / +2 / +3`."""
    draw = lambda seed, name: pn.derive_rng(seed, name).integers(0, 10**9, size=4).tolist()
    assert draw(20260808, "jsd_null") == draw(20260808, "jsd_null")
    assert draw(20260808, "jsd_null") != draw(20260808, "phi_ci")
    assert draw(20260808, "jsd_null") != draw(20260809, "jsd_null")


def test_stream_derivation_is_not_process_salted():
    """`hash()` on a str is salted per process; blake2b is not. Pinned literally."""
    assert pn.derive_rng(20260808, "jsd_null").integers(0, 10**9) == pn.derive_rng(
        20260808, "jsd_null"
    ).integers(0, 10**9)


def test_benjamini_hochberg_matches_hand_calculation():
    assert [round(v, 6) for v in pn.benjamini_hochberg([0.01, 0.02, 0.03, 0.5])] == [
        0.04,
        0.04,
        0.04,
        0.5,
    ]


def test_holm_matches_hand_calculation():
    assert [round(v, 6) for v in pn.holm([0.01, 0.02, 0.03, 0.5])] == [0.04, 0.06, 0.06, 0.5]


def test_bh_never_exceeds_holm():
    """The relationship that makes reporting both meaningful rather than decorative."""
    raw = [0.001, 0.004, 0.012, 0.04, 0.2, 0.35, 0.9]
    bh, hm = pn.benjamini_hochberg(raw), pn.holm(raw)
    assert all(b <= h + 1e-12 for b, h in zip(bh, hm))
    assert all(r <= b + 1e-12 for r, b in zip(raw, bh))  # and neither undoes the raw


def test_adjusted_values_are_monotone_in_raw():
    raw = [0.5, 0.001, 0.2, 0.04]
    for adjusted in (pn.benjamini_hochberg(raw), pn.holm(raw)):
        pairs = sorted(zip(raw, adjusted))
        assert all(pairs[i][1] <= pairs[i + 1][1] + 1e-12 for i in range(len(pairs) - 1))


def test_undefined_cells_leave_the_family_and_are_named():
    """m must be the tests actually performed; a silent drop shrinks every p."""
    grid = {("A", "N1"): 0.01, ("B", "N1"): float("nan"), ("C", "N1"): 0.5}
    adjusted, m, undefined = pn.adjust_family(grid)
    assert m == 2
    assert undefined == [("B", "N1")]
    assert adjusted[("B", "N1")]["bh"] != adjusted[("B", "N1")]["bh"]
    assert abs(adjusted[("A", "N1")]["bh"] - 0.02) < 1e-12  # 0.01 * 2/1


def test_family_is_the_whole_grid_not_one_class():
    """Correcting per class would treat three screens as three questions."""
    per_class = pn.benjamini_hochberg([0.01, 0.02])
    whole_grid = pn.benjamini_hochberg([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
    assert whole_grid[0] > per_class[0]


# --------------------------------------------------------------------------
# ADDITION, registered 2026-08-09 (readout-rule §2) -- TVD, the materiality scale
# --------------------------------------------------------------------------
# An addition, not a change to any rule above: JSD keeps significance, TVD
# carries materiality, and the moved/not-moved verdict lives in the read-out
# rule, never in the scorer.

def test_tvd_matches_the_readout_rules_worked_table():
    """The exact table printed in docs/readout-rule.md §2. If any row here moves,
    the registered document and the code disagree about what 0.10 means."""
    d = dv.total_variation
    assert abs(d({"buy": 1.0}, {"buy": 0.9, "hold": 0.1}) - 0.10) < 1e-12
    assert abs(d({"buy": 0.7, "hold": 0.3}, {"buy": 0.6, "hold": 0.4}) - 0.10) < 1e-12
    assert abs(d({"buy": 0.7, "hold": 0.3}, {"buy": 0.5, "hold": 0.5}) - 0.20) < 1e-12
    assert abs(d({"buy": 0.7, "hold": 0.3}, {"buy": 0.3, "hold": 0.7}) - 0.40) < 1e-12
    assert abs(d({"buy": 1.0}, {"sell": 1.0}) - 1.0) < 1e-12


def test_tvd_is_baseline_independent_where_jsd_is_not():
    """The property that made TVD the materiality scale: a 10-point shift is 0.10
    from ANY baseline, while the same shift's JSD depends on where it started --
    which is why a single JSD threshold under-flags unstable-baseline items."""
    ten_from_unanimous = dv.total_variation({"buy": 1.0}, {"buy": 0.9, "hold": 0.1})
    ten_from_split = dv.total_variation({"buy": 0.7, "hold": 0.3}, {"buy": 0.6, "hold": 0.4})
    assert abs(ten_from_unanimous - ten_from_split) < 1e-12
    jsd_unanimous = dv.jensen_shannon({"buy": 1.0}, {"buy": 0.9, "hold": 0.1})
    jsd_split = dv.jensen_shannon({"buy": 0.7, "hold": 0.3}, {"buy": 0.6, "hold": 0.4})
    assert abs(jsd_unanimous - jsd_split) > 0.01


def test_tvd_identity_symmetry_and_empty():
    assert dv.total_variation({"buy": 0.5, "sell": 0.5}, {"sell": 0.5, "buy": 0.5}) == 0.0
    a, b = {"buy": 0.7, "hold": 0.3}, {"buy": 0.2, "sell": 0.8}
    assert abs(dv.total_variation(a, b) - dv.total_variation(b, a)) < 1e-12
    empty = dv.total_variation({}, {"buy": 1.0})
    assert empty != empty  # NaN, the same stance as `disagreement` on <2 runs


# --------------------------------------------------------------------------
# END TO END -- the tie path against the log that actually contains a tie
# --------------------------------------------------------------------------

def test_neg_momentum_log_exercises_the_tie_path(tmp_path=None):
    """The handoff's named test case: S01's BASE is buy 2 / hold 1 / sell 2 there.

    Asserted on the REPORT rather than on internals, because the requirement is
    about what a reader sees: the exclusion named with its counts, the item still
    present in the JSD and baseline tables, and no flip rate quoted for it.
    """
    candidates = sorted(ROOT.glob("arms/*/data/runs/rehearsal_neg_momentum.jsonl"))
    if not candidates:  # pragma: no cover -- no arm carries the rehearsal log here
        return
    log = candidates[0]
    out = Path(tmp_path) / "tie.md" if tmp_path else log.parent / "_tie_check.md"
    # 200 draws: this case tests the tie path, not p-value resolution.
    assert sp.main(["--log", str(log), "--out", str(out), "--null-draws", "200"]) == 0
    report = out.read_text(encoding="utf-8")

    assert "Excluded from flip-rate scoring — tied baseline" in report
    assert "| S01 | {'buy': 2, 'sell': 2, 'hold': 1} | buy, sell |" in report
    assert "TIE (buy, sell)" in report          # baseline table names it
    assert "not interpretable (tied baseline)" in report
    assert "| S01 | 0.0913 |" in report          # still in the per-item JSD table
    assert "## MATERIALITY — total-variation distance" in report
    assert "### Per-item TVD" in report          # the read-out rule reads cells, not means
    out.unlink(missing_ok=True)


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL {name}: {exc}")
    print("all scoring rules pinned" if not failures else f"{failures} FAILED")
    raise SystemExit(1 if failures else 0)
