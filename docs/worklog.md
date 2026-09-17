# Worklog — reconstructed

**Written 2026-08-09, after the fact.** The FinMem arm's history landed in one
import commit (`a252dc9`); this document is the reconstruction of the work
sessions it contains, plus the monorepo-era work that followed. It is
documentation, not evidence — where a claim needs proof, the proof is named in
the entry's evidence field, and where there is no proof, the entry says
*recollection* and means it.

Entries are ordered by **track and dependency, not by calendar**. Work ran in
parallel across tracks, and some of it originated outside this repo and was
reproduced into it; a single timeline would fabricate an ordering that never
existed. Where "originated" and "landed" differ, both are stated — the landed
event is the checkable one.

## The clock

Calendar dates decorate; position relative to the boundary events is the
load-bearing claim. Four ticks so far, two pending:

| tick | event | anchor |
|---|---|---|
| **P** | pilot data exists — 630 rehearsal rows, 2026-08-08 → 2026-08-09 | log mtimes (`rehearsal_neg_momentum.jsonl` 08-08 12:09 through `rehearsal_replication.jsonl` 08-09 05:23); OSF Reg 1 disclosure |
| **R** | scoring rules frozen — tag `rules-registered-2026-08-09` | the tag and its 22-test suite |
| **M** | monorepo conversion, 2026-08-09 | commits `a252dc9`..`e095329` |
| **O** | OSF Registration 1 filed, 2026-09-17 | the OSF registration, <https://osf.io/ahcvt>; tag `reg1-filed-2026-09-17` |
| *F* | *fixture freeze / Registration 2 — pending* | |
| *C* | *confirmatory runs — pending* | |

Every entry below carries an epoch: **pre-P** (before any pilot row), **P→R**
(after pilot data, before the rules froze), or **post-R**. That coordinate is
the one a reviewer needs; nothing in the study turns on whether the wrapper
preceded the corpus builder.

Evidence grades: **anchored** (a timestamp or artifact outside anyone's memory),
**reconstructed** (inferred from artifacts, stated basis), **recollection**.

## Tracks

Dependency joins: T1+T2 feed T3; T3+T4 feed T5; T5's data feeds T6's registered
content; T6+T7 feed the registration. T4 never runs the agent — it and T3 were
genuinely parallel.

### T1 — Environment

- **Containerized environment: image, compose, key-gated entrypoint.**
  Dockerfile, compose, entrypoint refusing to start on missing keys, harness
  venv baked at `/opt/harness-venv`. Epoch pre-P, first substantive work in the
  arm repo. Evidence: reconstructed — everything downstream executes in this
  container, so it precedes all of it; repo scaffold dates to 2026-07-23
  (`0b8adc3`). Calendar: ~late July, recollection.

### T2 — Agent

- **Vendor FinMem at `be814aa`; freeze its dependency world.** Clone gitignored,
  pin recorded, poetry install onto the named `agent-venvs` volume,
  `finmem-lock.txt` committed. Epoch pre-P. Depends on T1 (the freeze is an
  in-container act; the clone alone wasn't). Evidence: anchored for the pin
  (clone's own `.git`), recollection for the date.
- **Backbone probe and config renderer.** `probe_backbone.py`,
  `render_config.py`, the rendered TOML proving published-default decoding
  against the dated backbone snapshot (`gpt-5.4-mini-2026-03-17`). Epoch pre-P.
  Could have preceded the vendor step — needs only the harness venv and a key;
  order between these two is not recoverable and doesn't matter.

### T3 — Wrapper & frozen contexts

- **The wrapper: one `decide()` per call against a restored frozen context.**
  `wrapper.py` snapshot/restores memory store, checkpoints and vector index
  every call; `verify_wrapper.py` proves the reset. Epoch pre-P.
- **Frozen contexts: smoke, flat and negative-momentum checkpoints.**
  `check_momentum.py`, the `ckpt_*` and `result_*` trees. Epoch pre-P.
- These two were **entangled, not ordered** — checkpoint generation runs the
  agent, the wrapper restores checkpoints; development interleaved. Recorded as
  a pair deliberately. Evidence: reconstructed from the artifacts; no basis for
  sequencing within the pair.

### T4 — Fixtures & corpus

Parallel to T3 throughout; writes memory-row pickles, never runs the agent.

- **Corpus builder, verified on the smoke tier.** `build_corpus.py`,
  `corpus_config.json`, `verify_corpus.py`, the 2-item smoke round-trip. Epoch
  pre-P.
- **Sanity tier.** SANITY-POS/NEG, BASE only — the positive control: does the
  agent respond to unambiguous signal at all. Epoch pre-P.
- **Rehearsal fixtures: borderline and replication tiers.** The 7 hand-written
  items the pilot ran against — the author's own, unaudited, and that fact later
  became the +0.317 directional-drift lesson. Epoch pre-P by construction
  (fixtures precede their runs). Evidence: anchored relative to P.

### T5 — Runner & pilot

- **Run matrix runner: append-only JSONL, stamped rows.** `run_matrix.py`;
  item, class, action, status, backbone version, context stamp; logs never
  edited. Epoch pre-P. Joins T3 and T4.
- **Pilot execution.** 630 rows, four rehearsal runs. **This is tick P.**
  Order within: neg-momentum 08-08, then flat / borderline / replication early
  08-09. Evidence: anchored (log mtimes). Logs uncommitted per data policy;
  reports regenerate from them by one command.

### T6 — Scoring

- **Scoring v1: φ, JSD net of control, item-level bootstrap.** First
  `score_pilot.py` — decoding floor, BASE-vs-FLOOR control, directional-shift
  diagnostic, marginal table, context-stamp pooling refusal. Epoch: straddles
  P — drafted against the runner's schema, hardened against real rows.
  *Originated* partly outside the repo (analysis drafting); *landed* pre-R.
  Evidence: reconstructed. The honest admission: scorer-before-any-data was the
  stronger posture and this only partly achieved it.
- **Pilot findings → gaps list → handoff.**
  `docs/handoff-item2-scoring-rules.md`: the S01 tie, the φ = 0.638
  uninterpretable flip rate, the 2,000-draw null with no multiplicity
  correction, converted to a scoped work order with the five open decisions
  flagged for the lead. Epoch P→R, necessarily — the doc quotes observed
  failures. Evidence: anchored (the doc; the failures it cites are in the logs).
- **Scoring rules per gaps item 2: tie rule, φ gate, formalized null.**
  `divergence.py`, `permutation_null.py`, the `score_pilot.py` rework,
  `test_scoring_rules.py`. Old quantities reproduce byte-identical; the S01 tie
  is the targeted test. **This is tick R** — tag `rules-registered-2026-08-09`.
  Evidence: anchored. The causal order pilot→rules is real, deliberate, and
  disclosed in Registration 1 — three rules were forced by observed failures
  and could not have been written blind.

- **TVD, the materiality scale (readout-rule §2's required addition).**
  `divergence.total_variation`, net-of-control summary and per-cell tables in
  `score_pilot.py`, the §2 worked table pinned verbatim in the test suite
  (25 tests from 22). An addition, not a change to any registered rule — but it
  obliges a re-tag: `rules-registered-2026-08-09` predates it, so the snapshot
  attached to Registration 1 must be the re-tagged one. Epoch post-R,
  2026-08-09. Anchored (the commit landing this entry's artifacts).

### T7 — Decisions & registration

- **Drop N2 for FinMem: the engine injects the ticker independently of the
  news.** `excluded_klasses` plus the builder's refuse-without-reason guard;
  rationale in the arm README citing `puppy/prompts.py:16`. Lead's decision,
  dated **2026-08-08** — anchored. The evidence for the drop was available from
  the moment of the clone; the decision floated to fixture-finalization. The
  lesson — audit the source seam *before* building fixtures against it — became
  gaps item 3 and was applied to both sibling engines before they run.
- **Applicability audit, all three engines.** `docs/applicability-audit.md`,
  the class × engine matrix; N2 dies on all three, generalized to a finding
  about identity-anchoring agents. Epoch post-R, 2026-08-09. Anchored
  (`f7790df`).
- **Read-out rule and OSF Registration 1 draft.** What each outcome licenses,
  fixed before confirmatory data. Epoch post-R, 2026-08-09. Anchored
  (`e095329`); in-flight edits continue past it.
- **Candidate-engine scan, and the scoping it forced.**
  `docs/candidate-scan.md`: four non-subject engines scouted at HEAD
  (provenance-graded as such); N2's drop generalizes 6-for-6 with the identity
  mechanism 7-for-7; attenuation split into transformation vs dilution;
  FinAgent's image channel confirmed not unique (QuantAgent/Xiong) and, being
  less attenuated than the news, made a named ground for scoping any FinAgent
  STABLE claim. Landed as readout-rule §4/§6.6–6.7/§8 edits, registered before
  confirmatory data. Epoch post-R, 2026-08-09. Anchored (the doc and the
  readout-rule diff in this entry's commit).

- **Applicability audit, material classes M1–M5, all three engines.**
  `docs/applicability-audit-material.md` and
  `docs/applicability-matrix-material.json`: fifteen cited class × engine cells
  under a five-verdict vocabulary (the null audit's three plus `no_target` and
  `undetermined`). FinMem: M1/M2/M3/M5 run, M4 no target. TradingAgents: M1/M2
  dropped — the fundamentals analyst fetches the quarterly income statement by
  ticker, N2's mechanism with a number in place of a name; M3/M5 run attenuated
  and scoped to content the engine has no independent source for; M4 no target.
  FinAgent: M1/M2/M3/M5 run attenuated under a no-future-rows precondition, M4
  no target (strategy documentation exists only in a config with no news
  channel). No cell undetermined. Four corrections to the filed null audit
  recorded without editing it: TradingAgents has four analysts, not five, and
  the news reaches two; five TradingAgents inputs bypass the vendor-registry
  interception point; its fine-grained lossy count is ≥ 3; FinAgent's K-line
  image carries fourteen post-decision days under `tools/main.py`
  (`finagent/plots/kline.py:32-33`), closed by the substituted price frame
  ending at the decision date. Harness prerequisites: FinMem's
  `check_numbers_preserved` rejects every material variant and must become
  class-aware; each arm must register its action alphabet. Source reading only,
  no engine run, all three clones verified at pin. Epoch post-R and
  post-Registration 1 (`reg1-snapshot-2026-08-16`), 2026-09-15. Evidence:
  anchored (the commit landing the two documents; every verdict cites pinned
  source lines). Undetermined cells: none — the two FinAgent preconditions
  (price frame ends at the decision date; template and entry point registered)
  are lead decisions enforceable at the registered interception point, not
  open verdicts, and are listed for Registration 2.

- **Mechanical citation verification, and Registration 1 amended for the
  FinAgent price-frame condition.** `scripts/verify_citations.py` resolves
  every citation in both applicability matrices at the recorded pin with
  `git show`, never the working tree; pin mismatch aborts; statuses ok /
  wide / missing_file / line_out_of_range / external; report at
  `docs/citation-check-report.md` with repo SHA, UTC date and the committed
  SHA-256 of each matrix; `tests/test_verify_citations.py` pins the
  behaviour. Result at filing: 240 citations, 234 ok, 5 wide, 1 external
  (upstream issue #814), none failing. Registration 1 draft amended before
  filing (edits, not deviations — nothing had been filed): the frozen-design
  framing; the FinAgent price-frame condition in the held-constant list;
  limitation 3 rewritten to separate the constant-channel limit from the
  post-decision-image contamination it does not remedy; the Registration 2
  any-party sentence; a scope note for the material audit; the verification
  sentence in reproducibility. Attachments 1–7 remain byte-identical to
  `reg1-snapshot-2026-08-16`; attachments 8–10 (material audit, its matrix,
  the citation report) are extracted from `reg1-filing-2026-09b`, and the
  filed worklog is the snapshot's, so this entry is not in it. A first
  filing tag, `reg1-filing-2026-09`, was cut and pushed before the read-out
  rule's PROPOSED constants had been ratified in the registration text and
  before the prior public report of the FinAgent K-line condition had been
  credited; it stays in history as the record of that, and is superseded by
  `reg1-filing-2026-09b`. Epoch
  post-R, pre-filing, 2026-09-15. Evidence: anchored (this commit and the
  filing tag).

- **FinAgent K-line lookahead: prior public report located; not sent.**
  `docs/finagent-lookahead-disclosure.md`. Source reading establishes that
  three upstream entry points (`tools/main.py`, `tools/main_mi_w_decision.py`,
  `tools/main_strategy.py`) call the K-line plotter without passing `mode`, so
  the validation-phase chart spans `look_forward_days = 14` sessions past the
  decision date, and that the upstream README's run instructions name two of
  them; whether the paper's reported figures came from those entry points is
  not recoverable from source and is not claimed. The author then located a
  prior public report of the same line (DVampire/FinAgent issue #2,
  2025-04-14, unanswered; repository dormant since 2024-08-31) and decided
  not to send a separate report. The audit is recorded as an independent
  confirmation, not a discovery; credit added to the material audit, its
  matrix, and registration limitation 3. Epoch post-R, pre-filing,
  2026-09-15. Evidence: anchored (this commit; every line cited is verifiable
  at the pin; the issue URL is external and dated).

- **Free analyses after the filing tag, all exploratory.** (1) N3 distractor
  incorporation, `scripts/analyze_n3_incorporation.py` →
  `docs/n3-incorporation-2026-09-15.md`: over the 125 pilot N3 rows the
  appended clause is named in 0 rationales (false-positive control 0/480),
  while the filler memory rows are named in up to 419/670; read as positional
  absorption, stated as a hypothesis. (2) The four pilot logs re-scored under
  the current SHA, `docs/rescoring-2026-09-15/`; frozen rules unchanged, 25
  scoring tests pass; the reports now carry the scoring SHA, TVD, the 10,000-
  draw null and the BH/Holm family. (3) Candidate scan extended on the
  mechanical sub-question only, `docs/candidate-scan-material-2026-09-15.md`:
  CryptoTrade, FinRobot, StockAgent, QuantHarness read at recorded commits;
  every engine with a news channel independently re-derives or receives in
  parallel the figures a material class would alter; a counterexample was
  sought per engine and none found; one new sub-type (parallel delivery)
  named. Epoch post-filing-tag, 2026-09-15. Evidence: scouting-grade for the
  scan (recorded commits, not pins); anchored for (1) and (2).

- **Registration 1 filed on OSF, 2026-09-17 — tick O.** <https://osf.io/ahcvt>.
  Changes made in the form relative to the draft, and carried back into
  `docs/osf-registration-1-analysis-plan.md` in this commit: the agent's
  rationale text added as a measured variable, recorded with no confirmatory
  analysis; derived quantities moved to the Indices field with explicit
  formulas; the three pilot-derived rules stated in the foreknowledge
  explanation; a statement on causal inference attached to Study design; the
  read-out rule's NOT SHOWN TO BE SENSITIVE and INCONCLUSIVE labels given a
  boundary at thresholds the rule already uses (CI lower bound on the class's
  net effect above 0, versus at or below 0), with SENSITIVE and STABLE reported
  together when both criteria hold; limitation 7 declares the registrant's
  position. Attachments uploaded as one bundle, `reg1-attachments.zip`
  (sha256 `ed048e6b377fceef30c04939667478c89c8feea60ffb04e12d280eb4dd9eb70a`),
  to stay within OSF's per-question file limit: the ten files extracted from
  `reg1-snapshot-2026-08-16` and `reg1-filing-2026-09b`, each verified against
  its tagged blob, plus `MANIFEST.txt` and `SHA256SUMS`. The bundle is not
  committed; it regenerates from the tags. Epoch post-R, post-filing,
  2026-09-17. Evidence: anchored (the OSF registration and its timestamp; tag
  `reg1-filed-2026-09-17`).

### T8 — Monorepo

- **Conversion: one repo, one arm per engine; scoring at the root.** The former
  `finperturb-finmem` repo rehomed entire as `arms/finmem`; TradingAgents and
  FinAgent cloned and pinned, no harnesses. Only the path assumptions the move
  broke were changed; 22/22 tests and a byte-identical report re-generation
  verified the rehoming. **This is tick M**, 2026-08-09. Anchored
  (`a252dc9`..`e095329`).

## What this log is not

Not a substitute for the history that should have existed — the thirteen-commit
breakdown this reconstruction follows is the lesson, not the repair. Nothing
here backdates anything: commit dates, tag dates and log mtimes stay what they
are, and where this document disagrees with an anchored artifact, the artifact
wins. Going forward the log is contemporaneous or it is nothing — a chunk gets
its entry (and its commit) at the boundary where you would later want to prove
what you knew.
