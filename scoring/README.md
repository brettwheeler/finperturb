# scoring/ — the pre-registered rules

The scoring rules of the FinPerturb study, as code. **One copy, every arm.**
Sharing them as one directory in one tree is what makes them a registration: two
arms cannot drift apart when there is nothing to drift between, and "both
engines were scored under the same rules" is answered by the repo SHA each
report prints in its *Scoring rules in force* table.

(History note: this directory spent one day, 2026-08-09, as a separate
`finperturb-core` repo vendored into arms by pinned submodule. The monorepo
conversion the same day made the pin machinery redundant; the subtree merge
preserved those commits, which carry the registration dates.)

```
score_pilot.py           reads an append-only run log, writes one markdown report
permutation_null.py      the null, its seed discipline, its multiplicity correction
divergence.py            distribution / JSD / disagreement — pure, shared by both
test_scoring_rules.py    pins the pre-registered rules (no API calls, ~1s)
```

## The contract

One JSONL row per run. This is the entire interface; nothing in this directory
may import from, or assume the layout of, any arm.

| field | meaning |
|---|---|
| `item_id` | which fixture item |
| `klass` | `FLOOR` \| `BASE` \| `N1` \| `N2` \| `N3` |
| `action` | the agent's decision (`buy` / `sell` / `hold`) |
| `status` | `ok`, or why not |
| `model_version` | backbone version string; a split forces a rerun |
| `context` | frozen-context stamp (dict); pooling across different stamps is refused |

## The three pre-registered rules

Settled by the project lead 2026-08-09, **before any real fixture existed**.
Changing any constant or procedure changes what the study measured: it is a new
registration, made deliberately, never an edit that still passes the tests.

1. **A tied baseline is excluded from flip-rate scoring** and retained in full
   for distributional scoring, named in the report with its counts. The baseline
   table also carries a **margin** (top-1 share minus top-2), because a 9-vs-8
   split is not a tie and is just as arbitrary.
2. **JSD + permutation null governs at every phi.** The flip rate is not
   promoted or demoted by band — it carries an interpretability verdict, and the
   report prints `not interpretable (phi = 0.46)` in place of the number when an
   item fails. Threshold `PHI_INTERPRETABLE_MAX = 0.20`, declared at the top of
   `score_pilot.py`, overridable by `--phi-interpretable-max` for sensitivity
   checks only.
3. **The null is 10,000 resamples**, one root seed with streams derived by NAME,
   and one multiplicity family over the whole item × class grid —
   Benjamini–Hochberg and Holm reported side by side, raw p never dropped.

## Running

From the repo root, against any arm's logs:

```bash
python scoring/score_pilot.py --log arms/finmem/data/runs/<run>.jsonl --out arms/finmem/data/runs/<report>.md
python -m pytest scoring/test_scoring_rules.py -q
```

The dirty-tree check in the provenance row is scoped to `scoring/` alone: an arm
mid-edit is ordinary life, an edited `scoring/` is a different registration and
is flagged as one.
