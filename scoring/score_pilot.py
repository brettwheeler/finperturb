#!/usr/bin/env python3
"""§7: read the append-only log, emit one markdown report. Reads nothing else.

Everything here is regenerable from the raw log by a single command, which is the
point: the log is never edited (§8.4), so every correction, exclusion and
definition lives in this file where a reader can check it.

This script REPORTS. It does not conclude. Whether the pilot passes is the project
lead's call against a read-out rule fixed before the runs started (§7), so there
is deliberately no verdict, no threshold and no pass/fail anywhere below.

THE FLOOR IS THE WHOLE ARGUMENT. The agent is stochastic by design, so some
proportion of "flips" are the model disagreeing with itself on input it has
already seen. phi measures that directly -- FLOOR rows are k repeats of identical
text -- and every flip rate is reported net of it. Without phi a flip rate is not
evidence of anything (§8.1).

BOOTSTRAP OVER ITEMS, NOT RUNS. Runs within an item share a headline, a baseline
and a memory state, so they are correlated; resampling runs would treat 5 reps of
one item as 5 independent observations and produce an interval several times too
narrow. Resampling items is the honest unit.

THREE SCORING RULES ARE PRE-REGISTERED, not chosen while reading the numbers.
They were settled by the project lead on 2026-08-09, before any real fixture
existed, and they are shared with every future engine so two engines' figures
are comparable:

  1. A TIED BASELINE IS EXCLUDED FROM FLIP-RATE SCORING and retained in full for
     distributional scoring. The rehearsal's S01 had a BASE of buy 2 / hold 1 /
     sell 2 -- an exact tie broken silently by `Counter.most_common` insertion
     order -- and that item's FLOOR showed buy at 1-in-10, so the arbitrary
     winner was a RARE action and the variants "flipped" 5/5 almost by
     construction. The baseline table now also carries a MARGIN, because a 9-vs-8
     split is not a tie and is just as arbitrary, and only the margin shows it.
  2. ONE STATISTIC GOVERNS EVERYWHERE: JSD with a permutation null. The flip rate
     is not promoted or demoted by phi -- it carries an INTERPRETABILITY verdict
     instead. Switching which statistic is primary by band would mean two engines
     reporting headline numbers from different statistics whenever their phi
     distributions differ, which is the comparability the rules exist to protect.
  3. The null itself, its seed discipline and its multiplicity correction live in
     `permutation_null.py` with the procedure written down.

THIS DIRECTORY IS THE ONE COPY OF THE RULES, shared by every arm of the
monorepo, because one tree cannot drift against itself. Every report prints the
repo SHA it ran at, so "both engines were scored under the same rules" is a
checkable fact rather than an assumption. Registered 2026-08-09 and tagged
`rules-registered-2026-08-09`; see scoring/README.md for what that tag is and
is NOT evidence of. Nothing in this directory may import from, or assume the layout
of, any arm: the contract is the log row (item_id / klass / action / status /
model_version / context) and nothing else.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from divergence import disagreement, distribution, jensen_shannon, total_variation
from permutation_null import NULL_DRAWS_DEFAULT, adjust_family, derive_rng, null_pvalue


def _head_from_files(start: Path) -> Optional[str]:
    """Read HEAD's SHA straight off the checkout, no git binary involved.

    A SHA is just bytes on disk, and reading them cannot be refused the way
    running git can -- `safe.directory` rejects a bind-mounted repo whose owner
    is not the container user, which is every Docker-on-Windows mount. Walks UP
    from this directory the way git itself does, because scoring/ sits inside
    the repo rather than being one; handles `.git` as a FILE (a worktree or
    submodule gitlink, `gitdir:` possibly relative) or a directory, and HEAD
    either detached (a bare SHA) or a ref, resolved through the loose ref file
    or packed-refs.
    """
    try:
        here = start
        while True:
            dotgit = here / ".git"
            if dotgit.exists():
                break
            if here.parent == here:
                return None
            here = here.parent
        if dotgit.is_file():
            line = dotgit.read_text(encoding="utf-8").strip()
            if not line.startswith("gitdir:"):
                return None
            gitdir = (here / line.split(":", 1)[1].strip()).resolve()
        else:
            gitdir = dotgit
        head = (gitdir / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref:"):
            return head[:7]  # detached HEAD -- a bare SHA
        ref = head.split(":", 1)[1].strip()
        loose = gitdir / ref
        if loose.is_file():
            return loose.read_text(encoding="utf-8").strip()[:7]
        packed = gitdir / "packed-refs"
        if packed.is_file():
            for entry in packed.read_text(encoding="utf-8").splitlines():
                if entry.endswith(" " + ref):
                    return entry.split(" ", 1)[0][:7]
        return None
    except (OSError, UnicodeDecodeError):
        return None


def core_version() -> str:
    """The repo SHA these rules ran at, for the provenance table.

    Asks git about THIS FILE's own directory; git walks up to the monorepo root,
    so the answer is the tree's SHA -- and in a monorepo the tree's SHA IS the
    rules' version, which is the comparability guarantee. The dirty check is
    scoped to scoring/ alone: an arm mid-edit is ordinary life and says nothing
    about the RULES, where an edited scoring/ is the difference between "these
    rules" and "these rules, edited". When git cannot answer (absent, or
    refusing the repo), the SHA is read off the checkout's own files and says
    so. Degrades to a stated unknown rather than failing the report -- but an
    unknown is printed as one, never guessed.
    """
    here = Path(__file__).resolve().parent
    try:
        sha = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if sha.returncode == 0:
            dirty = subprocess.run(
                ["git", "-C", str(here), "status", "--porcelain", "--", "."],
                capture_output=True, text=True, timeout=10,
            )
            suffix = " + uncommitted changes" if dirty.stdout.strip() else ""
            return sha.stdout.strip() + suffix
    except (OSError, subprocess.TimeoutExpired):
        pass
    from_files = _head_from_files(here)
    if from_files:
        return f"{from_files} (from HEAD file; dirty state unverified)"
    return "unknown (not a git checkout)"

VARIANT_KLASSES = ["N1", "N2", "N3"]
BOOTSTRAP_DRAWS = 10_000

# ROOT seed. Every generator below is derived from it BY NAME (see
# permutation_null.derive_rng), never by `RNG_SEED + 1 / +2 / +3`: arithmetic
# offsets renumber every later stream when an analysis is inserted in the middle,
# which silently changes intervals that have already been published.
RNG_SEED = 20260808

# PRE-REGISTERED. A flip rate is quotable only when the item's decoding floor is
# below this and its baseline is not a tie. Declared here rather than as a literal
# inside a branch, and printed in the report, so a run cannot quietly differ from
# the registration. On the rehearsal set only S01 (phi = 0.064) qualifies.
PHI_INTERPRETABLE_MAX = 0.20


def load_rows(log_path: Path) -> List[Dict[str, Any]]:
    rows = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def baseline_of(actions: List[str]) -> Dict[str, Any]:
    """The modal BASE action, the tie test, and the margin that shows a near-tie.

    RULE 1 lives here. `Counter.most_common(1)` answers a tie by insertion order,
    which is not a decision anyone made and cannot be defended in a report, so a
    tie returns action=None and the item drops out of flip-rate scoring upstream.
    It keeps every one of its BASE runs, so nothing changes for JSD.

    MARGIN is top-1 share minus top-2 share, and it exists because the tie test is
    binary while arbitrariness is not: 9-vs-8 passes the test and is worth no more
    than 8-vs-8. Reported, never acted on -- a second threshold on the margin would
    be a rule nobody registered.
    """
    counts = Counter(actions).most_common()
    total = sum(n for _, n in counts)
    top_n = counts[0][1]
    tied = [a for a, n in counts if n == top_n]
    second_n = counts[1][1] if len(counts) > 1 else 0
    return {
        "action": None if len(tied) > 1 else counts[0][0],
        "tied": sorted(tied) if len(tied) > 1 else [],
        "counts": dict(counts),
        "margin": (top_n - second_n) / total if total else float("nan"),
    }


def flip_verdict(item: str, phi_value: float, phi_max: float, tied: bool) -> Optional[str]:
    """None when this item's flip rate is quotable, else the reason it is not.

    RULE 2. A flip rate measured against an unstable baseline reports which
    baseline was drawn, not what the perturbation did -- so the report prints the
    reason in place of the number rather than printing a number with a warning
    beside it that a reader is free to skip.
    """
    if tied:
        return "not interpretable (tied baseline)"
    if phi_value != phi_value:
        return "not interpretable (no floor)"
    if phi_value >= phi_max:
        return f"not interpretable (phi = {phi_value:.3f})"
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--log",
        type=Path,
        required=True,
        nargs="+",
        help=(
            "one or more append-only logs. Several are pooled ONLY when they share a "
            "frozen context -- same checkpoint, decision date and price series -- because "
            "§7.4 bootstraps over items and items split across files give intervals "
            "computed on a fraction of the sample. Rows carry a context stamp and mixing "
            "two is refused."
        ),
    )
    parser.add_argument("--manifest", type=Path, help="corpus manifest, to report excluded classes")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--null-draws",
        type=int,
        default=NULL_DRAWS_DEFAULT,
        help=(
            f"resamples per permutation null (default {NULL_DRAWS_DEFAULT}, the final-run "
            "value). Lower it to iterate; the value used is printed in the report, and the "
            "smallest reportable p is 1/(draws+1), so a fast run cannot be mistaken for a "
            "final one."
        ),
    )
    parser.add_argument(
        "--phi-interpretable-max",
        type=float,
        default=PHI_INTERPRETABLE_MAX,
        help=(
            f"pre-registered decoding-floor ceiling for a QUOTABLE flip rate (default "
            f"{PHI_INTERPRETABLE_MAX}). The flag exists for sensitivity checks; moving it "
            "after seeing the numbers is choosing a rule to fit a result."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RNG_SEED,
        help=f"root seed; every stream is derived from it by name (default {RNG_SEED})",
    )
    args = parser.parse_args(argv)

    rows = []
    for log_path in args.log:
        rows.extend(load_rows(log_path))

    # Refuse to average two experiments. A row without a context stamp predates the
    # field; those are reported as unverifiable rather than assumed compatible,
    # because "no evidence of a mismatch" and "evidence of no mismatch" are not the
    # same claim and this is exactly where that distinction bites.
    contexts = {
        json.dumps(r["context"], sort_keys=True) for r in rows if isinstance(r.get("context"), dict)
    }
    unstamped = sum(1 for r in rows if not isinstance(r.get("context"), dict))
    if len(contexts) > 1:
        print("refusing to pool logs from different frozen contexts:", file=sys.stderr)
        for blob in sorted(contexts):
            print(f"  {blob}", file=sys.stderr)
        return 2

    ok = [r for r in rows if r["status"] == "ok"]
    not_ok = [r for r in rows if r["status"] != "ok"]

    versions = sorted({r["model_version"] for r in ok if r.get("model_version")})

    # per item
    floor_actions: Dict[str, List[str]] = defaultdict(list)
    base_actions: Dict[str, List[str]] = defaultdict(list)
    variant_actions: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for row in ok:
        if row["klass"] == "FLOOR":
            floor_actions[row["item_id"]].append(row["action"])
        elif row["klass"] == "BASE":
            base_actions[row["item_id"]].append(row["action"])
        else:
            variant_actions[row["item_id"]][row["klass"]].append(row["action"])

    items = sorted(set(floor_actions) | set(base_actions))
    phi_by_item = {i: disagreement(floor_actions[i]) for i in items if floor_actions[i]}
    phi = float(np.nanmean(list(phi_by_item.values()))) if phi_by_item else float("nan")

    # Per-item phi interval, resampling that item's own FLOOR RUNS.
    # This looks like it contradicts §7.4's "resample items, not runs" -- it does
    # not. That rule protects an estimate AGGREGATED across items from treating
    # correlated runs as independent. Here the quantity belongs to a single item,
    # and its runs are the only sample there is. Screening an item on a point
    # estimate from ten draws would repeat the mistake that produced a "buy"
    # baseline for an item whose floor said buy was a one-in-ten action.
    rng_phi = derive_rng(args.seed, "phi_ci")
    phi_ci: Dict[str, Any] = {}
    for item, actions in floor_actions.items():
        if len(actions) < 2:
            continue
        arr = np.array(actions)
        draws = [disagreement(list(rng_phi.choice(arr, size=len(arr), replace=True))) for _ in range(BOOTSTRAP_DRAWS)]
        phi_ci[item] = tuple(float(v) for v in np.percentile(draws, [2.5, 97.5]))

    # §7.2 the baseline a variant is compared against, plus RULE 1's tie test.
    # A tied item keeps every BASE run and therefore stays in every JSD table
    # below; what it loses is a modal baseline, which is a flip rate's only
    # possible reference.
    baseline_info = {i: baseline_of(base_actions[i]) for i in items if base_actions[i]}
    baseline = {i: b["action"] for i, b in baseline_info.items() if b["action"] is not None}
    tied_items = {i: b for i, b in baseline_info.items() if b["tied"]}

    # §7.3 per item per klass, so the bootstrap can resample items
    flips_by_item: Dict[str, Dict[str, List[int]]] = defaultdict(dict)
    for item in items:
        for klass in VARIANT_KLASSES:
            actions = variant_actions[item].get(klass, [])
            if actions and item in baseline:
                flips_by_item[item][klass] = [int(a != baseline[item]) for a in actions]

    # RULE 2's verdict, per item. Computed once and used by both flip-rate tables.
    flip_reason = {
        item: flip_verdict(
            item,
            phi_by_item.get(item, float("nan")),
            args.phi_interpretable_max,
            tied=item in tied_items,
        )
        for item in items
    }
    interpretable = {i for i in items if flip_reason[i] is None}

    rng = derive_rng(args.seed, "flip_bootstrap")
    summary = {}
    for klass in VARIANT_KLASSES:
        contributing = [i for i in items if klass in flips_by_item.get(i, {})]
        if not contributing:
            continue
        raw = float(np.mean([np.mean(flips_by_item[i][klass]) for i in contributing]))

        # phi over the CONTRIBUTING items, not over all items. §7.3 says
        # net = raw - phi and §7.1 defines phi as the mean over items, which are
        # the same thing once every item carries every class -- as they will with
        # the real fixture set. They diverge only when a class covers a subset,
        # and then the global mean corrects a rate measured on some items using a
        # floor measured on others. The bootstrap already resamples contributing
        # items, so using the global mean here also made the point estimate and
        # its interval disagree. Both now use the same set.
        phi_contributing = float(np.nanmean([phi_by_item[i] for i in contributing if i in phi_by_item]))
        net = raw - phi_contributing

        # resample ITEMS; phi is recomputed on the same resample so the net rate
        # is not corrected by a constant borrowed from the full sample
        draws = []
        for _ in range(BOOTSTRAP_DRAWS):
            picked = rng.choice(contributing, size=len(contributing), replace=True)
            r = np.mean([np.mean(flips_by_item[i][klass]) for i in picked])
            p = np.nanmean([phi_by_item.get(i, np.nan) for i in picked])
            draws.append(r - p)
        low, high = np.percentile(draws, [2.5, 97.5])
        summary[klass] = {
            "n_items": len(contributing),
            "n_runs": sum(len(flips_by_item[i][klass]) for i in contributing),
            "raw": raw,
            "phi": phi_contributing,
            "net": net,
            "ci": (float(low), float(high)),
            # How much of this aggregate is made of items whose own flip rate is
            # quotable. An aggregate over uninterpretable items inherits their
            # problem; the count is the only thing that says so on the row itself.
            "n_interpretable": sum(1 for i in contributing if i in interpretable),
        }

    # PRIMARY STATISTIC: distributional shift.
    #
    # A modal flip rate breaks exactly where the phenomenon is strongest: an item
    # the agent is easily moved on has a high phi, and a high phi means its modal
    # baseline is a coin flip, so the flip rate reports which baseline was drawn.
    # JSD compares the whole action distribution and needs no stable mode, so it
    # measures the same thing with an instrument that survives the interesting case.
    #
    # And it needs its own floor. FLOOR and BASE rows are the SAME text run
    # separately, so the divergence between THEIR distributions is the divergence
    # you get when nothing was perturbed at all -- pure sampling. Every variant
    # divergence is reported net of it. That is §8.1's rule ("flip rates net of the
    # floor") carried intact into the new statistic rather than quietly dropped
    # along with the old one.
    jsd_control = {
        item: jensen_shannon(distribution(base_actions[item]), distribution(floor_actions[item]))
        for item in items
        if base_actions[item] and floor_actions[item]
    }

    jsd_by_klass: Dict[str, Dict[str, float]] = defaultdict(dict)
    for item in items:
        if not base_actions[item]:
            continue
        base_dist = distribution(base_actions[item])
        for klass in VARIANT_KLASSES:
            actions = variant_actions[item].get(klass, [])
            if actions:
                jsd_by_klass[klass][item] = jensen_shannon(distribution(actions), base_dist)

    # Permutation p-value per item per class, against the item's own same-input
    # pool. RULE 3: the procedure, the seed derivation and both corrections live in
    # permutation_null.py; this is only the grid.
    rng_null = derive_rng(args.seed, "jsd_null")
    jsd_pvalue: Dict[str, Dict[str, float]] = defaultdict(dict)
    pvalue_grid: Dict[Any, float] = {}
    for klass in VARIANT_KLASSES:
        for item, observed in jsd_by_klass.get(klass, {}).items():
            pool = list(floor_actions[item]) + list(base_actions[item])
            value = null_pvalue(
                pool,
                n_variant=len(variant_actions[item][klass]),
                n_base=len(base_actions[item]),
                observed=observed,
                rng=rng_null,
                draws=args.null_draws,
            )
            jsd_pvalue[klass][item] = value
            pvalue_grid[(item, klass)] = value

    # ONE family across the whole item x class grid. Correcting per class would
    # treat three screens as three separate questions and correct each too gently.
    adjusted, n_tests, undefined_cells = adjust_family(pvalue_grid)

    # MATERIALITY SCALE: total-variation distance, per cell, net of the same
    # BASE-vs-FLOOR control as JSD -- the addition the read-out rule's §2
    # requires before registration. TVD is linear in action-share change and
    # baseline-independent, so its threshold means the same thing on a unanimous
    # item and a 70/30 one, which is exactly where a single JSD threshold fails.
    # It carries no p-value and governs nothing here: significance stays with
    # JSD's permutation null, and the moved/not-moved verdict lives in
    # docs/readout-rule.md, not in this report.
    tvd_control = {
        item: total_variation(distribution(base_actions[item]), distribution(floor_actions[item]))
        for item in items
        if base_actions[item] and floor_actions[item]
    }
    tvd_by_klass: Dict[str, Dict[str, float]] = defaultdict(dict)
    for item in items:
        if not base_actions[item]:
            continue
        base_dist = distribution(base_actions[item])
        for klass in VARIANT_KLASSES:
            actions = variant_actions[item].get(klass, [])
            if actions:
                tvd_by_klass[klass][item] = total_variation(distribution(actions), base_dist)

    rng_tvd = derive_rng(args.seed, "tvd_bootstrap")
    tvd_summary = {}
    for klass in VARIANT_KLASSES:
        per_item = tvd_by_klass.get(klass, {})
        contributing = sorted(per_item)
        if not contributing:
            continue
        raw = float(np.mean([per_item[i] for i in contributing]))
        control = float(np.nanmean([tvd_control.get(i, np.nan) for i in contributing]))
        draws = []
        for _ in range(BOOTSTRAP_DRAWS):
            picked = rng_tvd.choice(contributing, size=len(contributing), replace=True)
            r = np.mean([per_item[i] for i in picked])
            c = np.nanmean([tvd_control.get(i, np.nan) for i in picked])
            draws.append(r - c)
        low, high = np.percentile(draws, [2.5, 97.5])
        tvd_summary[klass] = {
            "n_items": len(contributing),
            "raw": raw,
            "control": control,
            "net": raw - control,
            "ci": (float(low), float(high)),
        }

    rng_jsd = derive_rng(args.seed, "jsd_bootstrap")
    jsd_summary = {}
    for klass in VARIANT_KLASSES:
        per_item = jsd_by_klass.get(klass, {})
        contributing = sorted(per_item)
        if not contributing:
            continue
        raw = float(np.mean([per_item[i] for i in contributing]))
        control = float(np.nanmean([jsd_control.get(i, np.nan) for i in contributing]))
        draws = []
        for _ in range(BOOTSTRAP_DRAWS):
            picked = rng_jsd.choice(contributing, size=len(contributing), replace=True)
            r = np.mean([per_item[i] for i in picked])
            c = np.nanmean([jsd_control.get(i, np.nan) for i in picked])
            draws.append(r - c)
        low, high = np.percentile(draws, [2.5, 97.5])
        jsd_summary[klass] = {
            "n_items": len(contributing),
            "raw": raw,
            "control": control,
            "net": raw - control,
            "ci": (float(low), float(high)),
        }

    lines: List[str] = []
    add = lines.append
    add("# FinPerturb pilot — FinMem\n")
    add("Logs:\n")
    for log_path in args.log:
        add(f"- `{log_path}`")
    add(f"\nRows: {len(rows)} ({len(ok)} ok, {len(not_ok)} not ok)\n")

    if contexts:
        add(f"Frozen context: `{sorted(contexts)[0]}`\n")
    if unstamped:
        add(f"**{unstamped} rows carry no context stamp** (written before the field existed).")
        add("Their frozen context cannot be verified from the data; that they belong here")
        add("rests on how they were run, not on what was recorded.\n")

    # The rules are pre-registered, so the report states which ones were in force
    # rather than leaving a reader to infer them from the numbers. A report whose
    # constants cannot be read off it is not reproducible from the logs alone.
    add("\n## Scoring rules in force\n")
    add("| rule | value |")
    add("|---|---|")
    add(f"| scoring code | finperturb `{core_version()}` |")
    add("| tied baseline | excluded from flip-rate scoring, retained for JSD |")
    add("| governing statistic | JSD + permutation null, at every phi |")
    add("| materiality scale | net TVD per cell: variant vs base, minus the BASE-vs-FLOOR control |")
    add(f"| flip rate quotable when | phi < {args.phi_interpretable_max} and baseline not tied |")
    add(f"| permutation resamples | {args.null_draws:,} (smallest reportable p = {1 / (args.null_draws + 1):.4f}) |")
    add(f"| root seed | {args.seed} (streams derived by name) |")
    add(f"| bootstrap draws | {BOOTSTRAP_DRAWS:,} |")
    add("| multiplicity | Benjamini-Hochberg and Holm, one family over item x class |")
    if args.null_draws < NULL_DRAWS_DEFAULT:
        add(f"\n**Iteration run**: {args.null_draws:,} resamples, below the {NULL_DRAWS_DEFAULT:,} ")
        add("final-run value. p-values here are coarser than a final report's.\n")
    add("")

    if len(versions) == 1:
        add(f"Model version: `{versions[0]}` (single version across all scored rows)\n")
    else:
        add(f"**MODEL VERSION SPLIT: {versions}** — §6.3 requires discarding rows from the ")
        add("superseded version and rerunning them. The numbers below mix versions.\n")

    if args.manifest and args.manifest.exists():
        with args.manifest.open("r", encoding="utf-8") as handle:
            excluded = json.load(handle).get("excluded_klasses", {})
        if excluded:
            add("## Classes not run\n")
            for klass, detail in sorted(excluded.items()):
                add(f"- **{klass}** — {detail['cells_dropped']} cells not built. {detail['reason']}\n")

    add("\n## Decoding floor (phi)\n")
    add(f"phi = **{phi:.4f}** (mean over {len(phi_by_item)} items)\n")
    add("\n| item | n | floor actions | phi | 95% CI (resampling this item's runs) |")
    add("|---|---|---|---|---|")
    for item in sorted(phi_by_item):
        counts = dict(Counter(floor_actions[item]))
        low, high = phi_ci.get(item, (float("nan"), float("nan")))
        add(f"| {item} | {len(floor_actions[item])} | {counts} | {phi_by_item[item]:.4f} | [{low:.4f}, {high:.4f}] |")
    add("\nAn item whose phi is high cannot support a flip statistic: its modal baseline is")
    add("a coin flip, so a flip rate measured against it reflects which baseline was drawn")
    add("rather than what the perturbation did. This is no longer left to the reader to")
    add(f"screen — a flip rate is gated on phi < {args.phi_interpretable_max} and printed as")
    add("a reason rather than a number when it fails. Nothing here gates the JSD tables,")
    add("which need no stable mode and are reported for every item.\n")

    add("\n## PRIMARY — distributional shift (Jensen–Shannon, bits)\n")
    add("Variant action distribution vs the base item's, net of the same-input control.")
    add("The control is BASE vs FLOOR: identical text, so its divergence is sampling noise")
    add("and nothing else. 0 bits = identical distributions, 1 bit = disjoint.\n")
    add("| klass | items | raw JSD | control JSD | net | 95% CI (bootstrap over items) |")
    add("|---|---|---|---|---|---|")
    for klass in VARIANT_KLASSES:
        if klass in jsd_summary:
            s = jsd_summary[klass]
            add(
                f"| {klass} | {s['n_items']} | {s['raw']:.4f} | {s['control']:.4f} | {s['net']:+.4f} | "
                f"[{s['ci'][0]:+.4f}, {s['ci'][1]:+.4f}] |"
            )
        else:
            add(f"| {klass} | 0 | — | — | — | not run |")

    # §7.5 is explicit that the spread is the statistic, not the mean: one item
    # swinging hard is the finding, and averaging it against nineteen quiet ones
    # is how it gets lost.
    add("\n### Per-item JSD, with permutation p-values\n")
    add(f"p is the share of {args.null_draws:,} same-input resamples reaching the observed")
    add("divergence — i.e. how often the unperturbed text alone produces a shift this large at")
    add("these sample sizes. The spread across items is the statistic §7.5 asks for; the mean")
    add("hides the one item that moved.\n")
    add(f"Each cell reads `JSD (raw p / BH / Holm)`. The family is all {n_tests} item × class")
    add("tests corrected together, not each class on its own. Raw p is kept beside the")
    add("adjusted values and is never dropped: BH controls the false discovery rate and suits")
    add("the screen's actual question (which items moved), Holm controls the family-wise error")
    add("rate and is the one to read if a single cell would be quoted on its own.\n")
    if undefined_cells:
        add(f"{len(undefined_cells)} cell(s) had no defined p and are excluded from the family")
        add(f"of {n_tests}: {', '.join(f'{i}/{k}' for i, k in sorted(undefined_cells))}.\n")
    add(
        "| item | control (BASE vs FLOOR) | "
        + " | ".join(f"{k} (raw / BH / Holm)" for k in VARIANT_KLASSES)
        + " |"
    )
    add("|---|---|" + "---|" * len(VARIANT_KLASSES))
    for item in sorted(items):
        cells = []
        for klass in VARIANT_KLASSES:
            if item in jsd_by_klass.get(klass, {}):
                value = jsd_by_klass[klass][item]
                adj = adjusted.get((item, klass), {})
                cells.append(
                    f"{value:.4f} ({adj.get('raw', float('nan')):.3f} / "
                    f"{adj.get('bh', float('nan')):.3f} / {adj.get('holm', float('nan')):.3f})"
                )
            else:
                cells.append("—")
        control = f"{jsd_control[item]:.4f}" if item in jsd_control else "—"
        add(f"| {item} | {control} | " + " | ".join(cells) + " |")

    add("\n## MATERIALITY — total-variation distance\n")
    add("TVD is the read-out rule's materiality scale: the share of runs that would have")
    add("to land on a different action to explain the shift, so 0.10 always means a tenth")
    add("of runs decided differently — on a unanimous baseline and a 70/30 one alike,")
    add("which is the linearity JSD does not have. It carries no p-value: significance")
    add("lives in the JSD tables above, materiality lives here, and the read-out rule")
    add("requires BOTH before a cell is declared moved. This report, as ever, declares")
    add("nothing.\n")
    add("| klass | items | raw TVD | control TVD | net | 95% CI (bootstrap over items) |")
    add("|---|---|---|---|---|---|")
    for klass in VARIANT_KLASSES:
        if klass in tvd_summary:
            s = tvd_summary[klass]
            add(
                f"| {klass} | {s['n_items']} | {s['raw']:.4f} | {s['control']:.4f} | {s['net']:+.4f} | "
                f"[{s['ci'][0]:+.4f}, {s['ci'][1]:+.4f}] |"
            )
        else:
            add(f"| {klass} | 0 | — | — | — | not run |")

    add("\n### Per-item TVD\n")
    add("Each cell reads `raw (net)`, where net subtracts THIS item's own BASE-vs-FLOOR")
    add("control — identical text, so the TVD sampling alone produces at these run")
    add("counts. The read-out rule's materiality criterion is applied to the net value,")
    add("per cell, by the lead — never by this script.\n")
    add(
        "| item | control (BASE vs FLOOR) | "
        + " | ".join(f"{k} raw (net)" for k in VARIANT_KLASSES)
        + " |"
    )
    add("|---|---|" + "---|" * len(VARIANT_KLASSES))
    for item in sorted(items):
        cells = []
        for klass in VARIANT_KLASSES:
            if item in tvd_by_klass.get(klass, {}):
                value = tvd_by_klass[klass][item]
                control_value = tvd_control.get(item, float("nan"))
                cells.append(f"{value:.4f} ({value - control_value:+.4f})")
            else:
                cells.append("—")
        control = f"{tvd_control[item]:.4f}" if item in tvd_control else "—"
        add(f"| {item} | {control} | " + " | ".join(cells) + " |")

    add("\n## SECONDARY — modal flip rates\n")
    add("Retained because it is the statistic §6–§7 were designed around and it is")
    add("legible. It does not govern anything: JSD is primary at every phi, and a flip")
    add("rate is quotable only for an item that passes the interpretability gate below.\n")

    if tied_items:
        add("### Excluded from flip-rate scoring — tied baseline\n")
        add("A tie has no modal action, and picking one by dictionary order would make every")
        add("flip rate for that item a measure of the tie-break. These items keep all their")
        add("BASE runs and appear in full in every JSD table above.\n")
        add("| item | BASE actions | tied on |")
        add("|---|---|---|")
        for item in sorted(tied_items):
            info = tied_items[item]
            add(f"| {item} | {info['counts']} | {', '.join(info['tied'])} |")
        add("")

    add("### Per-item flip rate, gated\n")
    add(f"Quotable when phi < {args.phi_interpretable_max} and the baseline is not tied;")
    add("otherwise the reason is printed in place of the number, because a rate measured")
    add("against an unstable baseline reports which baseline was drawn rather than what the")
    add("perturbation did.\n")
    add(f"{len(interpretable)} of {len(items)} items pass.\n")
    add("| item | phi | " + " | ".join(VARIANT_KLASSES) + " |")
    add("|---|---|" + "---|" * len(VARIANT_KLASSES))
    for item in sorted(items):
        phi_cell = f"{phi_by_item[item]:.4f}" if item in phi_by_item else "—"
        reason = flip_reason[item]
        cells = []
        for klass in VARIANT_KLASSES:
            # "not run" and "not interpretable" are different claims and must not
            # share a cell: a class with no runs for this item has nothing being
            # withheld, and printing the gate's reason there would invent a
            # measurement that was never made.
            has_runs = bool(variant_actions[item].get(klass))
            if not has_runs:
                cells.append("—")
            elif reason is not None:
                cells.append(reason)
            else:
                runs = flips_by_item[item][klass]
                cells.append(f"{float(np.mean(runs)):.4f} (n={len(runs)})")
        add(f"| {item} | {phi_cell} | " + " | ".join(cells) + " |")
    add("")

    add("### Aggregate flip rate\n")
    add("`interpretable` counts how many of the contributing items pass the gate. An")
    add("aggregate built mostly from items that fail it inherits their problem — the")
    add("number is printed rather than suppressed because it is an input to nothing, but")
    add("it is not quotable on a row where that count is short of the item count.\n")
    add(
        "| klass | items | interpretable | runs | raw | phi (these items) | net (raw − phi) | "
        "95% CI (bootstrap over items) |"
    )
    add("|---|---|---|---|---|---|---|---|")
    negative_net = False
    short_of_gate = False
    for klass in VARIANT_KLASSES:
        if klass in summary:
            s = summary[klass]
            negative_net = negative_net or s["net"] < 0
            short_of_gate = short_of_gate or s["n_interpretable"] < s["n_items"]
            add(
                f"| {klass} | {s['n_items']} | {s['n_interpretable']}/{s['n_items']} | {s['n_runs']} | "
                f"{s['raw']:.4f} | {s['phi']:.4f} | "
                f"{s['net']:+.4f} | [{s['ci'][0]:+.4f}, {s['ci'][1]:+.4f}] |"
            )
        else:
            add(f"| {klass} | 0 | 0/0 | 0 | — | — | — | not run |")
    if short_of_gate:
        add("\nAt least one class aggregates items whose own flip rate is not interpretable.")
        add("Read the per-item table above and the PRIMARY JSD table instead.\n")
    if negative_net:
        add("\nA negative net rate is not negative instability. It means the variants agreed")
        add("with their item's baseline MORE often than two runs on identical input agree")
        add("with each other — the perturbation moved the decision less than the agent's own")
        add("sampling does.\n")
    if len(items) < 3:
        add(f"\nThe bootstrap resamples items and there are {len(items)}, so the interval is")
        add("degenerate rather than precise. Intervals are uninformative below roughly 10 items.\n")

    add("\n## Baseline actions\n")
    add("`margin` is the top action's share minus the runner-up's. The tie test is binary")
    add("and arbitrariness is not: a 9-vs-8 split passes the test and is worth barely more")
    add("than 8-vs-8, and only the margin shows it. Reported, not acted on — no rule was")
    add("pre-registered against it.\n")
    add("| item | baseline (modal BASE) | margin | BASE actions |")
    add("|---|---|---|---|")
    for item in sorted(baseline_info):
        info = baseline_info[item]
        shown = info["action"] if info["action"] is not None else f"TIE ({', '.join(info['tied'])})"
        add(f"| {item} | {shown} | {info['margin']:+.3f} | {info['counts']} |")

    for klass in VARIANT_KLASSES:
        values = sorted(jsd_by_klass.get(klass, {}).values())
        if values:
            add(f"\n{klass} JSD spread: min {values[0]:.4f} / median {float(np.median(values)):.4f} / max {values[-1]:.4f}")
    add("")

    # DIRECTIONAL DIAGNOSTIC — not in §7, and the most important thing added here.
    #
    # JSD measures how far a distribution moved, never which way. Instability is
    # directionless by nature: rewording should push some items toward buy and
    # others toward sell, and the mean shift per action should sit near zero even
    # when the magnitudes are large. A CONSISTENT direction across items is the
    # signature of something else -- variants that are systematically more
    # positive or more negative than their originals, i.e. a failure of §4.2's
    # meaning preservation that §4.3's audit was supposed to catch.
    #
    # Without this table, a set of badly-drifted paraphrases produces a large,
    # significant JSD and reads as a finding.
    add("\n## Directional shift (diagnostic, not in §7)\n")
    add("Mean change in each action's share, variant minus base, averaged over items.")
    add("Near-zero means the perturbation moved decisions in no consistent direction —")
    add("what instability looks like. A large consistent shift points at the VARIANTS")
    add("rather than the agent, and should be read as a fixture-quality alarm.\n")
    all_actions = sorted({r["action"] for r in ok if r["action"]})
    add("| klass | " + " | ".join(f"Δ {a}" for a in all_actions) + " | max abs |")
    add("|---|" + "---|" * (len(all_actions) + 1))
    for klass in VARIANT_KLASSES:
        deltas: Dict[str, List[float]] = defaultdict(list)
        for item in items:
            actions = variant_actions[item].get(klass, [])
            if not actions or not base_actions[item]:
                continue
            vd, bd = distribution(actions), distribution(base_actions[item])
            for action in all_actions:
                deltas[action].append(vd.get(action, 0.0) - bd.get(action, 0.0))
        if not deltas:
            continue
        means = {a: float(np.mean(deltas[a])) for a in all_actions}
        worst = max(abs(v) for v in means.values())
        add(
            f"| {klass} | " + " | ".join(f"{means[a]:+.3f}" for a in all_actions) + f" | {worst:.3f} |"
        )
    add("")

    # Not in §7's list. Added because a flip rate cannot distinguish a stable
    # agent from one that returns the same action to everything, and those are
    # different findings with identical numbers.
    add("\n## Marginal action distribution (addition to §7)\n")
    add("| klass | actions |")
    add("|---|---|")
    for klass in ["FLOOR", "BASE"] + VARIANT_KLASSES:
        actions = [r["action"] for r in ok if r["klass"] == klass]
        if actions:
            add(f"| {klass} | {dict(Counter(actions))} |")
    add("\nA degenerate distribution here makes a low flip rate uninformative: an agent")
    add("that answers the same way to everything cannot flip.\n")

    if not_ok:
        add("\n## Non-ok rows\n")
        add(f"| status | count |")
        add("|---|---|")
        for status, count in sorted(Counter(r["status"] for r in not_ok).items()):
            add(f"| {status} | {count} |")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"phi={phi:.4f} over {len(phi_by_item)} items; klasses scored: {sorted(summary)}")
    print(
        f"flip-rate gate: {len(interpretable)}/{len(items)} items interpretable "
        f"(phi < {args.phi_interpretable_max}); {len(tied_items)} excluded for a tied baseline"
    )
    print(f"permutation null: {args.null_draws:,} draws over {n_tests} tests, seed {args.seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
