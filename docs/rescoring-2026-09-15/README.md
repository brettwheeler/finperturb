# Pilot runs re-scored under the current scoring tag

Re-scored 2026-09-15 with `scoring/score_pilot.py` at the repository SHA each
report prints in its *Scoring rules in force* table (the filing state,
`reg1-filing-2026-09` lineage). The four raw logs are the fabricated-fixture
rehearsal runs disclosed in Registration 1 (§ Existing data); they are not
tracked in git (`arms/finmem/.gitignore`, run logs), so the reports are kept
here where the logs' original reports could not be.

What changed against the reports produced on 2026-08-09 at
`rules-registered-2026-08-09`: the TVD materiality scale (read-out rule §2),
the 10,000-draw permutation null with the 1/(draws+1) floor, and the
Benjamini–Hochberg plus Holm family over the item × class grid, all of which
landed at `reg1-snapshot-2026-08-16`. No frozen rule changed; the test suite
that pins them passes. These are instrument-development rows; nothing here is a
finding, and no row is ever pooled with confirmatory data.

Regenerate:

    python scoring/score_pilot.py --log arms/finmem/data/runs/rehearsal_<name>.jsonl --out docs/rescoring-2026-09-15/rehearsal_<name>_report.md
