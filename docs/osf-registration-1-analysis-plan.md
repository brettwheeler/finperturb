# OSF Registration 1 — analysis plan

**Status: DRAFT for the project lead.** Fields follow the OSF Preregistration
template. Registration 2 (confirmatory design: frozen fixtures, run matrix) is a
separate registration made at fixture freeze, before any confirmatory run.

**Attach to the registration (ten files).** Attachments 1–7 are byte-identical
to tag `reg1-snapshot-2026-08-16` (commit `3f5be87`); attachments 8–10 postdate
that tag and are extracted from tag `reg1-filing-2026-09b`.

1. `scoring-snapshot-reg1-2026-08-16.zip` — the authoritative rules snapshot
2. `readout-rule.md`
3. `applicability-audit.md`
4. `applicability-matrix.json`
5. `candidate-scan.md` (cited by the read-out rule §6.6; scouting-grade and
   labelled as such in its own header)
6. `worklog.md` (the provenance reconstruction, evidence grades included)
7. `ai-disclosure.md`
8. `applicability-audit-material.md` — postdates the snapshot (audited
   2026-09-15); included because it establishes the FinAgent price-frame
   design condition
9. `applicability-matrix-material.json`
10. `citation-check-report.md` — every source citation in attachments 4 and 9
    verified mechanically against the pinned clones by
    `scripts/verify_citations.py`

Public, no embargo.

---

## Title

FinPerturb: decision stability of published LLM trading agents under
meaning-preserving perturbation of news input

## Authors

Brett E Wheeler

## Description

Published LLM trading agents report buy/sell/hold decisions from news and price
context. This study asks whether such an agent changes its decision when the news
is reworded **without changing its meaning**, and reports every effect net of the
rate at which the agent disagrees with **itself** on identical input.

That second half is the design's core. These agents sample at default decoding
settings, so a proportion of apparent "flips" is the model disagreeing with
itself, not responding to the perturbation. The study measures that decoding
floor (φ) directly, by running identical text repeatedly, and reports every
effect relative to it. Without φ, a flip rate is not evidence of anything.

Three engines are examined, each in its own isolated harness against its own
pinned upstream source, with no modification to the agent:

| engine | paper | pin |
|---|---|---|
| FinMem | arXiv 2311.13743 | `be814aa` |
| TradingAgents | arXiv 2412.20138 | `a33fd4c` |
| FinAgent | arXiv 2402.18485 | `17248a0` |

The design is frozen and complete. The registrant does not have confirmatory
runs scheduled; this registration fixes the confirmatory design in advance of
data collection by any party. The channel-applicability audits attached here
establish, per engine and per class, which perturbations can express their
manipulation against that engine's input path, and are a precondition on
executing the suite rather than a step within it.

## Hypotheses

Framed per engine; the study is descriptive-with-inference rather than
theory-testing, and the read-out rule (attached) fixes what each outcome licenses.

- **H1.** A meaning-preserving paraphrase (N1) changes the action distribution
  beyond the decoding floor.
- **H2.** Appending an irrelevant, semantically null sentence (N3) changes the
  action distribution beyond the decoding floor.
- **H3 (registered as an architectural prediction, not a robustness claim).**
  Effect magnitude orders as FinMem > FinAgent > TradingAgents, following the
  number of lossy stages between the perturbed text and the decision, established
  by source audit before any data. Observing this ordering is *not* evidence that
  the later engines are more robust; observing it violated is a genuine finding.

No directional hypothesis is offered about *which way* decisions move.
Instability is directionless by nature, and a consistent direction across items
is pre-registered as a **fixture-quality alarm** rather than a result.

---

## Design plan

**Study type:** observational / computational experiment. No human participants.

**Blinding:** not applicable to the agents. The variant-generation model is a
different provider from the backbone under test (separate credential,
`PARAPHRASE_API_KEY`), so the model being tested does not author its own
perturbations.

**Design:** fully within-item. Each item is run under every applicable class
against one frozen context, so each item is its own control. Cells:

| class | perturbation |
|---|---|
| BASE | the original news text |
| FLOOR | the original text, run again as a separate block — the decoding floor |
| N1 | meaning-preserving paraphrase |
| ~~N2~~ | ~~entity rename~~ — **dropped on all three engines**, see below |
| N3 | original text plus an appended irrelevant sentence |

BASE and FLOOR are the same text run as two separate blocks. The divergence
between them is therefore pure sampling noise, and it is the control every
variant effect is reported net of.

**Perturbation applicability is established by source audit before any run.**
The protocol, the class × engine matrix and every citation are attached
(`docs/applicability-audit.md`). Its findings:

- **N2 is dropped for all three engines.** Each injects instrument identity —
  ticker, and in two cases company name, sector, industry and a business
  description — into the prompt independently of the news text, deliberately, so
  a renamed variant produces a self-contradictory prompt rather than a
  meaning-preserving rewrite. FinAgent additionally instructs the model to strip
  the asset name from its own extracted insights, erasing the perturbation. This
  is reported as a **general finding** about testing agents that anchor identity
  outside the text, not as a per-engine omission.
- **N1 and N3 run on all three, attenuated differently**, which is what H3
  encodes.

A companion audit of the five material perturbation classes across the same
three engines is attached (`docs/applicability-audit-material.md`). This
registration does not register a material-class design; the audit is included
because it establishes the FinAgent price-frame condition below, because it
records that the M4 class has no target on any engine audited, and because the
record should show what was known at filing. Any material-class confirmatory
design is a separate registration.

**Engine modification:** none. Fixtures are injected at each engine's own
sanctioned seam — memory rows (FinMem), a registered data vendor
(TradingAgents), the processed-data pipeline (FinAgent).

**Memory reset:** no run may remember a sibling variant. Each engine's reset
mechanism is verified before its runs, and the verification is reported.

**Held constant:** backbone model version (a dated snapshot, not a floating
alias), decoding settings at each engine's published defaults, the frozen context
(checkpoint, decision date, price series) stamped on every row, and — for FinAgent
— **the visual channel**, which is a design condition rather than an incidental
detail, because that engine sends chart images to the model and this study
perturbs text only.

**FinAgent price-frame condition.** For the FinAgent arm, the substituted price
frame supplied at the registered interception point terminates at the decision
date. Under the engine's base entry point the K-line plot is not informed that
it is out of training mode and can render up to fourteen post-decision sessions
into the image sent to the backbone; holding the visual channel constant across
cells does not remedy this, because a contaminated baseline contaminates every
comparison drawn against it. All FinAgent verdicts and all FinAgent results are
stated under this precondition.

---

## Sampling plan

### Existing data — DISCLOSED

**Data have been collected before this registration, and they materially shaped
the analysis plan.** Specifically:

A pilot of 630 rows was run on the FinMem arm between 2026-08-08 and 2026-08-09,
using **fabricated fixtures** (7 hand-written items, synthetic price series, no
real market data) with **the author's own unaudited variants**, against
`gpt-5.4-mini-2026-03-17`. It was instrument development, logged as such at the
time, and produced no findings.

**Three of the registered analysis rules were derived from it**, each forced by a
specific observed failure:

1. **The tie rule.** A pilot item returned a BASE of `buy 2 / hold 1 / sell 2` —
   an exact tie, broken silently by `Counter.most_common` insertion order — and
   its floor showed the "winning" action at 1-in-10. Every flip rate for that item
   was computed against an arbitrary, rare baseline. The rule now excludes a tied
   baseline from flip-rate scoring and retains it for distributional scoring.
2. **The φ interpretability gate.** At φ = 0.638 the modal flip rate put a class
   at net +0.062 — indistinguishable from noise — while JSD with a permutation
   null gave p = 0.028. A flip rate structurally cannot measure a high-φ item,
   because its baseline is a coin flip.
3. **The permutation-null procedure.** The pilot ran 2,000 resamples, floored
   p-values at 0.0005 while reporting one as 0.000, seeded streams by arithmetic
   offset, and applied no multiplicity correction to what will be a 60-cell grid.

The pilot also exposed a **fixture** problem rather than an agent one: its
hand-written paraphrases pushed +0.317 toward buy consistently across items, which
is the signature of drifted variants. That is why §4.2's numeric gate and §4.3's
audit are required for confirmatory variants, and why the directional-shift
diagnostic is retained.

**No pilot row will be pooled with confirmatory data.** This is enforced
mechanically: every row carries a frozen-context stamp and the scorer refuses to
pool rows whose stamps differ. Pilot results will be reported as instrument
development, separately and labelled.

No confirmatory data have been collected. The confirmatory fixture set does not
yet exist.

### Data collection procedures

Each engine runs in its own container against its own pinned source. For each
item: k FLOOR repeats of identical text, k BASE runs, and k runs of each variant
in each applicable class, all against one frozen context. Every run appends one
JSON row to an append-only log carrying item, class, action, status, backbone
model version and context stamp. **Logs are never edited**; every correction lives
in scoring code where a reader can check it.

### Sample size

Item count, repeats per cell and variants per class are fixed in **Registration 2**
at fixture freeze, sized against per-engine φ measured beforehand by a
**floor-only** pilot — repeats of identical input, generating no variant data.

Target: 20 items. The bootstrap resamples **items**, not runs, because runs within
an item share a headline, a baseline and a memory state; resampling runs would
treat repeats as independent and produce intervals several times too narrow.
Intervals over fewer than roughly 10 items are uninformative and are reported as
such.

Registration 2 — fixture freeze, item count, repeats and variants per class —
may be filed by any party executing this design, in their own account. Nothing
in this registration commits any party to a date for it.

### Stopping rule

The full matrix is run to completion. **No interim analysis.** The scorer runs
once, on the complete data. Any run against partial data is operational only, is
logged as such, and informs no decision.

If the backbone model version changes mid-run, every affected row is discarded and
rerun — the scorer detects and reports a version split.

---

## Variables

**Measured (per run):** the agent's action — `buy`, `sell` or `hold`; run status;
backbone model version; frozen-context stamp.

**Derived:**

| quantity | definition |
|---|---|
| φ (decoding floor) | `1 − Σp²` over an item's FLOOR actions: the probability two runs of identical input disagree |
| action distribution | action shares within a cell |
| JSD | Jensen–Shannon divergence in bits, variant vs base |
| control JSD | BASE vs FLOOR — identical text, so pure sampling noise |
| net JSD | JSD − control JSD |
| TVD | total-variation distance, variant vs base, net of control — the materiality scale |
| modal flip rate | share of variant runs differing from the modal BASE action — **secondary, and gated** |

**Manipulated:** perturbation class (BASE / FLOOR / N1 / N3).

---

## Analysis plan

The rules below are **already implemented and pinned** in `scoring/`, with a
test suite that fails if any constant or procedure changes. The rules froze at
tag `rules-registered-2026-08-09`; one **addition** landed after it — TVD, the
materiality scale §2 of the read-out rule required, pinned by its own tests and
changing no frozen rule — so the snapshot attached here is tag
`reg1-snapshot-2026-08-16`, which contains both. Both tags predate any
confirmatory run. The attached snapshot is authoritative; this section
describes it.

### Statistical model

**Primary: distributional shift.** Per cell, the JSD between the variant action
distribution and the item's BASE distribution, reported net of the BASE-vs-FLOOR
control. JSD is primary at every φ because it needs no stable mode, so it survives
the high-φ items where a flip rate structurally cannot work.

**Significance:** a permutation null per cell, built by resampling that item's own
pooled same-input draws (FLOOR + BASE) into two independent samples **of the
observed sizes** — sizes matter, since JSD between small samples is larger on
average by sampling alone. 10,000 resamples; the smallest reportable p is
1/(draws+1). Resampling is with replacement because a class can have more runs
than the same-input pool has draws.

Because the null is built from **each item's own floor pool**, the procedure
self-corrects for decoding noise: a high-φ item automatically produces a wider
null and requires a larger shift to reach significance.

**Multiplicity:** one family over the whole item × class grid — not per class,
which would treat several screens as independent questions and correct each too
gently. Benjamini–Hochberg **and** Holm are reported side by side with the raw p;
BH governs the read-out rule (the grid asks *which* items moved, so FDR control is
the right trade), Holm is reported for any cell quoted standalone. Raw p is never
dropped. Cells with an undefined p leave the family and are **counted and named**.

**Seeds:** one root seed; every analysis stream derived from it **by name** via a
SeedSequence, so a report is reproducible from the logs and the root seed alone,
and inserting an analysis cannot shift the streams of existing ones.

**Intervals:** bootstrap over **items**, 10,000 draws, with φ recomputed on each
resample so the net figure is not corrected by a constant borrowed from the full
sample.

### Secondary and diagnostic

- **Modal flip rate** — retained for legibility, governs nothing. It is quotable
  only for an item whose baseline is not tied **and** whose φ < 0.20; otherwise
  the report prints the reason in place of the number.
- **Directional shift** — mean change in each action's share, across items.
  Near-zero is what instability looks like. A large consistent direction is
  pre-registered as a **fixture-quality alarm**, not a finding.
- **Marginal action distribution** — distinguishes a stable agent from one that
  answers the same way to everything; those are different findings with identical
  flip rates.
- **Baseline margin** — top-1 share minus top-2, reported per item, because the
  tie test is binary and arbitrariness is not.

### Inference criteria

Fixed in `docs/readout-rule.md` (attached), in summary:

- A **cell has moved** when BH-adjusted p < 0.05 **and** net TVD ≥ 0.10 — both,
  never either. TVD rather than JSD for materiality because JSD is not linear in
  action-share change and depends on the baseline, so one JSD threshold would
  under-flag movement on unstable-baseline items.
- An **engine is sensitive** when ≥ 3 cells moved spanning ≥ 2 distinct items.
- An **engine is stable** only on an equivalence test — the 95% CI upper bound
  below the materiality threshold over ≥ 15 items. Not finding movement is
  reported as **not shown to be sensitive**, which is weaker and says so.
- An engine with **median φ ≥ 0.50** is reported as decoding-unstable and carries
  no effect claim.
- **Cross-engine magnitude** is confounded by attenuation (H3) and is reported
  only with that stated. Qualitative sensitivity is comparable; magnitude is not.

### Data exclusion

- Non-`ok` rows are excluded and **counted by status** in the report.
- Rows from a superseded backbone version are discarded and rerun.
- A tied baseline excludes that item from flip-rate scoring only; it is retained
  in full for all distributional analysis.
- Rows whose frozen-context stamp differs are never pooled — refused by the
  scorer, not by discipline.
- **No silent caps.** Anything excluded is counted and named in the report.

### Missing data

A cell that fails to produce a run is reported as a missing cell with its count,
never imputed and never silently dropped from a denominator.

### Exploratory analysis

Anything not above is exploratory and will be labelled as such in any write-up.
The sensitivity flags (`--phi-interpretable-max`, `--null-draws`, `--seed`) exist
for declared sensitivity analyses, always reported **alongside** the registered
value and never in place of it.

---

## Other

**Reproducibility.** Each engine is pinned by commit and never modified. Each
arm's container is a lockfile for everything below Python. The scoring code is one
copy shared by all arms; every report prints the SHA it ran at, so "both engines
were scored under the same rules" is checked rather than assumed. Every reported
figure regenerates from the raw logs by one command. Every source citation in
both applicability matrices is verified mechanically against the pinned clones
by `scripts/verify_citations.py`, whose report is attached. Verification
resolves each cited path at the recorded pin rather than in the working tree.

**Attachment provenance.** Attachments 1–7 are byte-identical to tag
`reg1-snapshot-2026-08-16` (commit `3f5be87`); attachments 8–10 postdate that
tag and are extracted from tag `reg1-filing-2026-09b`.

**Ratification of the read-out rule.** The attached read-out rule carries the
drafting header under which it was written, and marks four constants as
PROPOSED: the moved-cell criterion (BH-adjusted p < 0.05 and net TVD ≥ 0.10),
the sensitivity criterion (≥ 3 cells moved spanning ≥ 2 distinct items), the
stability criterion (95% CI upper bound below the materiality threshold over
≥ 15 items), and the decoding-instability threshold (median φ ≥ 0.50). Those
are the values stated in § Inference criteria above. The attachment is filed
unaltered so that it remains byte-identical to the snapshot; the act of filing
this registration ratifies the PROPOSED values as the registered values.

**Known limitations, registered rather than discovered:**

1. **N2 is untestable** against all three engines (see Design plan).
2. **Attenuation confounds cross-engine magnitude** (H3).
3. **Visual channel, FinAgent.** The engine is multimodal: base64 K-line
   payloads with moving-average and Bollinger overlays reach the backbone as
   image content, so a text-only perturbation exercises one channel of a
   two-channel agent. Two consequences are registered. First, the visual
   channel is held constant across all cells, and φ and JSD for this engine
   are reported with that limit stated (read-out rule §4, §6.7). Second, and
   separately, the image can carry post-decision price action under the
   engine's base entry point; the design condition in § Design plan closes
   this at the interception point, and results from this arm are valid only
   under that condition. The condition was reported publicly upstream on
   2025-04-14 (FinAgent issue #2) without maintainer response; this study's
   audit independently confirms that report. Whether the upstream published
   experiments used the affected entry point is not established by source
   reading alone and is not claimed here.
4. **Fabricated-fixture pilot** informed the analysis rules (see Existing data).
5. **Single backbone model version** per run matrix; results do not generalize
   across backbones.
6. **Registration dates in an author-controlled repository are a record, not
   proof.** This OSF registration is the third-party timestamp that git history
   cannot provide.
