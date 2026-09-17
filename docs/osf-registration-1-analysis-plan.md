# OSF Registration 1 — analysis plan

**Status: FILED 2026-09-17.** OSF registration: <https://osf.io/ahcvt>

This document is the repository copy of the filed registration. Field text is
transcribed verbatim from the registration, field by field, under the OSF
Preregistration template's headings; only list formatting is restored. Where
this document and the filed registration disagree, the filed registration wins.
Registration 2 (confirmatory design: frozen fixtures, run matrix) is a separate
registration made at fixture freeze, before any confirmatory run.

**Attachments.** One file, `reg1-attachments.zip`, uploaded to the Statistical
models question, containing the ten attachments below plus `MANIFEST.txt`
(source tag, commit and path per file, and regeneration commands) and
`SHA256SUMS`. Attachments 1–7 are byte-identical to tag
`reg1-snapshot-2026-08-16` (commit `3f5be87`); attachments 8–10 come from tag
`reg1-filing-2026-09b` (commit `5bd17d9`). The snapshot zip is
`git archive --format=zip reg1-snapshot-2026-08-16 scoring/`, which rebuilds
byte-identically. A second file, `Statement on direct inference on causal
relationships.txt`, is attached to the Study design question; its text is
reproduced under that heading below.

1. `scoring-snapshot-reg1-2026-08-16.zip` — the authoritative rules snapshot
2. `readout-rule.md`
3. `applicability-audit.md`
4. `applicability-matrix.json`
5. `candidate-scan.md`
6. `worklog.md`
7. `ai-disclosure.md`
8. `applicability-audit-material.md`
9. `applicability-matrix-material.json`
10. `citation-check-report.md`

Public, no embargo.

---

## Metadata

### Title

FinPerturb: decision stability of published LLM trading agents under
meaning-preserving perturbation of news input

### Description

Published LLM trading agents report buy/sell/hold decisions from news and price context. This study asks whether such an agent changes its decision when the news is reworded without changing its meaning, and reports every effect net of the rate at which the agent disagrees with itself on identical input. That second half is the design's core. These agents sample at default decoding settings, so a proportion of apparent "flips" is the model disagreeing with itself, not responding to the perturbation. The study measures that decoding floor (φ) directly, by running identical text repeatedly, and reports every effect relative to it. Without φ, a flip rate is not evidence of anything. Three engines are examined, each in its own isolated harness against its own pinned upstream source, with no modification to the agent: FinMem (arXiv 2311.13743, commit be814aa), TradingAgents (arXiv 2412.20138, commit a33fd4c) and FinAgent (arXiv 2402.18485, commit 17248a0). The analysis design is frozen; fixture-level parameters are fixed in a second registration. The registrant does not have confirmatory runs scheduled; this registration fixes the confirmatory design in advance of data collection by any party. The channel-applicability audits attached here establish, per engine and per class, which perturbations can express their manipulation against that engine's input path, and are a precondition on executing the suite rather than a step within it.

### Contributors

Brett E Wheeler

### License

CC-BY Attribution 4.0 International

### Subjects

Artificial Intelligence and Robotics; Finance; Social and Behavioral Sciences;
Computer Sciences; Economics; Physical Sciences and Mathematics

### Tags

algorithmic trading; FinPerturb; LLM agents; perturbation testing;
preregistration; robustness

---

## Overview

### Research questions or hypotheses

Framed per engine; the study is descriptive-with-inference rather than theory-testing, and the read-out rule (attached) fixes what each outcome licenses.

- H1. A meaning-preserving paraphrase (N1) changes the action distribution beyond the decoding floor.
- H2. Appending an irrelevant, semantically null sentence (N3) changes the action distribution beyond the decoding floor.
- H3 (registered as an architectural prediction, not a robustness claim). Effect magnitude orders as FinMem > FinAgent > TradingAgents, following the number of lossy stages between the perturbed text and the decision, established by source audit before any data. Observing this ordering is not evidence that the later engines are more robust; observing it violated is a genuine finding.

No directional hypothesis is offered about which way decisions move. Instability is directionless by nature, and a consistent direction across items is pre-registered as a 'fixture-quality alarm' rather than a result.

### Foreknowledge of data or evidence

Authors have observed the data, but have not performed the proposed analyses. At least some of the data that will be used for this analysis plan has been accessed and observed by the authors. The authors have sufficiently observed relevant evidence to influence their analysis decisions or conclusions. However, the authors have not yet performed any of the proposed analyses in this plan and will not do so until after this plan is registered.

### Explanation of foreknowledge and managing unintended influences

No data that will be analysed under this plan exist. The option above is selected as the most conservative fit because related pilot evidence has been observed and the scoring pipeline has been executed on it. Pilot rows are excluded from this plan's analyses by construction.

The foreknowledge is bounded and is stated precisely so that its limits can be checked. It consists of one pilot of 630 rows on one engine (FinMem) against one backbone, using fabricated fixtures and the author's own unaudited variants, run 2026-08-08 to 2026-08-09 as instrument development. No confirmatory data exist; the confirmatory fixture set has not been constructed. Two of the three engines in this design have never been run at all, so for TradingAgents and FinAgent there is no foreknowledge of any kind.

The scoring pipeline described in this plan — Jensen–Shannon divergence with a permutation null, Benjamini–Hochberg adjustment, bootstrap intervals over items, and flip rates net of the decoding floor — was executed on that pilot data in order to debug the scorer and to settle the analysis rules.

Three registered rules were derived from that pilot, each forced by an observed failure. (1) Tie rule: one item returned a BASE of buy 2 / hold 1 / sell 2, an exact tie broken silently by insertion order, and its floor showed the "winning" action at 1 in 10; a tied baseline is now excluded from flip-rate scoring and retained for distributional scoring. (2) φ interpretability gate: at φ = 0.638 the modal flip rate put a class at net +0.062, indistinguishable from noise, while JSD with a permutation null gave p = 0.028; flip rates are now reported only where φ < 0.20. (3) Permutation-null procedure: the pilot ran 2,000 resamples, floored p-values at 0.0005 while reporting one as 0.000, seeded streams by arithmetic offset, and applied no multiplicity correction; the registered procedure corrects each. The pilot also exposed a fixture problem rather than an agent one: the author's hand-written paraphrases shifted decisions +0.317 toward buy consistently across items, the signature of drifted variants, which is why confirmatory variants must pass the nullity gate and audit and why the directional-shift diagnostic is retained.

The following measures were taken to limit what that foreknowledge can do to the confirmatory result.

Every rule derived from the pilot is conservative with respect to the hypothesis. The tie rule excludes from flip-rate scoring exactly those items whose arbitrary baselines produced near-certain flips; the φ interpretability gate withholds flip rates on unstable items rather than quoting them; the permutation-null procedure adds multiplicity correction to a grid that previously had none; and the directional-shift diagnostic exists to attribute a consistent shift to the author's own variants rather than to the agent. Each makes instability harder to claim, not easier. This is verifiable from the rules themselves rather than asserted.

The rules were frozen in code before confirmatory data can exist. They live in a single directory shared by every arm, are pinned by a test suite, and are tagged (rules-registered-2026-08-09, reg1-snapshot-2026-08-16). Every report prints the repository SHA it ran at, so the claim that two engines were scored under identical rules is checkable rather than assumed. Registered constants — the interpretability threshold, the root seed, the bootstrap and null draw counts — are declared as named values and printed in every report, so a run cannot silently differ from this registration. Random streams are derived by name rather than by arithmetic offset, so inserting an analysis cannot renumber streams already reported.

Scoring is separated from conclusion. The scorer emits no verdict, no threshold and no pass or fail. What an outcome licenses is fixed by a read-out rule written before any confirmatory run and attached to this registration.

Pilot and confirmatory data cannot be pooled. Every row carries a frozen-context stamp and the scorer refuses to pool rows whose stamps differ. Pilot results will be reported separately and labelled as instrument development.

Fixture-level parameters are deferred. Item count, repeats per cell and variants per class are fixed in Registration 2 at fixture freeze, sized against per-engine φ measured by a floor-only pilot that repeats identical input and generates no variant data. The decoding floor is therefore measured without observing any perturbation effect.

Analysis runs once. The full matrix is run to completion with no interim analysis; logs are append-only and every correction lives in scoring code where it is visible.

Class applicability was decided from source, not from outcomes. The attached audits determine which perturbation classes can express their manipulation against each engine by reading pinned source, with no engine executed. Every verdict carries a file and line citation, and the citations are verified mechanically against the recorded pins by an attached script, so an applicability decision cannot be adjusted after seeing a result.

---

## Research design

### Study type

Simulation study: Using existing or synthetic data to assess performance of a model, mimic operation of an existing or proposed system, or predict possible outcomes in a controlled context. This may include demonstration of methods, many varieties of modeling, prediction of policy impacts, simulating behavior or outcomes in a population, and other designs.

### Intention for causal interpretation

Direct inference on causal relationship(s): This study is intended to infer or estimate a causal relationship between two or more variables. It is designed specifically for the purposes of causal inference or identification.

### Blinding of experimental treatments

No blinding is involved.

### Additional blinding during research or analysis

Blinding not applicable to the agents. The variant-generation model is a different provider from the backbone under test (separate credential, PARAPHRASE_API_KEY), so the model being tested does not author its own perturbations.

### Study design

Study type: simulation study — repeated execution of pinned agent software against frozen contexts and controlled input variants. No human participants.

Design: fully within-item. Each item is run under every applicable class against one frozen context, so each item is its own control. Cells:

- BASE — the original news text.
- FLOOR — the original text, run again as a separate block; the decoding floor.
- N1 — meaning-preserving paraphrase.
- N3 — original text plus an appended irrelevant sentence.
- N2 (entity rename) was specified but is dropped on all three engines; see below.

BASE and FLOOR are the same text run as two separate blocks. The divergence between them is therefore pure sampling noise, and it is the control every variant effect is reported net of.

Perturbation applicability is established by source audit before any run. The protocol, the class × engine matrix and every citation are attached (applicability-audit.md and applicability-matrix.json, in reg1-attachments.zip). Its findings:

- N2 is dropped for all three engines. Each injects instrument identity — ticker, and in two cases company name, sector, industry and a business description — into the prompt independently of the news text, deliberately, so a renamed variant produces a self-contradictory prompt rather than a meaning-preserving rewrite. FinAgent additionally instructs the model to strip the asset name from its own extracted insights, erasing the perturbation. This is reported as a general finding about testing agents that anchor identity outside the text, not as a per-engine omission.
- N1 and N3 run on all three, attenuated differently, which is what H3 encodes.

A companion audit of the five material perturbation classes across the same three engines is attached (applicability-audit-material.md and applicability-matrix-material.json, in reg1-attachments.zip). This registration does not register a material-class design; the audit is included because it establishes the FinAgent price-frame condition below, because it records that the M4 class has no target on any engine audited, and because the record should show what was known at filing. Any material-class confirmatory design is a separate registration.

Engine modification: none. Fixtures are injected at each engine's own sanctioned seam — memory rows (FinMem), a registered data vendor (TradingAgents), the processed-data pipeline (FinAgent).

Memory reset: no run may remember a sibling variant. Each engine's reset mechanism is verified before its runs, and the verification is reported.

Held constant: backbone model version (a dated snapshot, not a floating alias), decoding settings at each engine's published defaults, the frozen context (checkpoint, decision date, price series) stamped on every row, and — for FinAgent — the visual channel, which is a design condition rather than an incidental detail, because that engine sends chart images to the model and this study perturbs text only.

FinAgent price-frame condition. For the FinAgent arm, the substituted price frame supplied at the registered interception point terminates at the decision date. Under the engine's base entry point the K-line plot is not informed that it is out of training mode and can render up to fourteen post-decision sessions into the image sent to the backbone; holding the visual channel constant across cells does not remedy this, because a contaminated baseline contaminates every comparison drawn against it. All FinAgent verdicts and all FinAgent results are stated under this precondition.

**Attached file — Statement on direct inference on causal relationships.txt:**

> The design identifies the causal effect of a semantically null perturbation on an agent's decision distribution. Perturbation class is manipulated directly; the comparison is within-item against that item's own baseline; the frozen context, backbone model version and decoding settings are held constant by construction; and memory is reset between runs so that no cell can influence another. BASE and FLOOR are the same text executed as two separate blocks, so the divergence between them is sampling noise alone and is the control every perturbation effect is reported net of.
>
> The effect identified is bounded to the engine, backbone version and frozen context under which it is measured. No claim is made about language models in general, about trading performance, or about behavior under conditions other than those registered.

### Randomization

Not applicable. There is no assignment to randomize: every item is run under every applicable class against one frozen context, so each item is its own control (see Manipulated variables).

---

## Sampling

### Data collection procedures

Units and population. The unit of analysis is a news item. The population is financial news text of the kind each engine natively consumes; the sampling frame, inclusion and exclusion criteria, and item-type stratification are fixed in Registration 2 at fixture freeze. Items are constructed or selected so that no item references a price level or event dated after the decision date of the frozen context it is run against. Fixtures are constructed rather than drawn from a live feed where contamination control requires it; the basis is recorded at freeze.

Sources. Three engines, each at a pinned commit, each in its own container against its own pinned source, injected at that engine's sanctioned seam — memory rows (FinMem), a registered data vendor (TradingAgents), the processed-data pipeline (FinAgent). Backbone: a dated model snapshot, not a floating alias.

Procedure. For each item: k FLOOR repeats of identical text, k BASE runs, and k runs of each variant in each applicable class, all against one frozen context. Memory is reset between runs so that no run can remember a sibling variant; each engine's reset is verified before its runs and the verification is reported. Every run appends one JSON row to an append-only log carrying item, class, action, status, backbone model version and context stamp. Logs are never edited; every correction lives in scoring code where a reader can check it.

Exclusions. Rows whose status is not ok are excluded from scoring and reported by status. Rows spanning a mid-run backbone version change are discarded and rerun.

Duration. Determined by the executing party at fixture freeze; not fixed here.

### Sample size

Item count, repeats per cell and variants per class are fixed in Registration 2 at fixture freeze, sized against per-engine φ measured beforehand by a floor-only pilot — repeats of identical input, generating no variant data.

Target: 20 items. The bootstrap resamples items, not runs, because runs within an item share a headline, a baseline and a memory state; resampling runs would treat repeats as independent and produce intervals several times too narrow. Intervals over fewer than roughly 10 items are uninformative and are reported as such.

Registration 2 — fixture freeze, item count, repeats and variants per class — may be filed by any party executing this design, in their own account. Nothing in this registration commits any party to a date for it.

### Sample size rationale

Fixed in Registration 2 against per-engine φ measured by the floor-only pilot. The target of 20 items reflects two registered constraints: a STABLE verdict requires at least 15 contributing items, and item-level bootstrap intervals over fewer than roughly 10 items are uninformative.

### Starting and stopping rules

Starting. Confirmatory collection begins only after: the fixture set is frozen and registered in Registration 2; the variant nullity gate and audit have been passed for that set; each engine's memory reset has been verified; and per-engine φ has been measured by a floor-only pilot. Pilot and instrument-development runs carry a distinct frozen-context stamp and cannot be pooled with confirmatory rows — the scorer refuses to pool rows whose stamps differ. No confirmatory row exists before the Registration 2 filing.

Stopping. The full matrix is run to completion. No interim analysis. The scorer runs once, on the complete data. Any run against partial data is operational only, is logged as such, and informs no decision.

If the backbone model version changes mid-run, every affected row is discarded and rerun — the scorer detects and reports a version split.

---

## Variables

### Manipulated variables

Manipulated: perturbation class, four levels — BASE (the original news text), FLOOR (the same original text executed as a separate block, which measures the decoding floor), N1 (meaning-preserving paraphrase), N3 (the original text plus one appended irrelevant sentence). N2 (entity rename) is dropped on all three engines by source audit.

No randomization. There is no assignment to randomize: the design is fully within-item and exhaustive — every item is run under every applicable class against one frozen context, so each item serves as its own control. Levels differ only in the text supplied; the frozen context, backbone snapshot, decoding settings and memory state are held constant across all four.

### Measured variables

Measured (per run): the agent's action — buy, sell or hold; the agent's stated rationale text where the engine emits one; run status; backbone model version; frozen-context stamp.

Rationale text is recorded but no confirmatory analysis of it is registered here; any analysis of rationale content is exploratory under Other planned analysis.

### Indices

All derived quantities are computed per cell (one cell = one item under one perturbation class, within one engine) from the actions recorded across that cell's completed runs. Actions are {buy, sell, hold}.

- Action distribution: p_c(a) = n_c(a) / n_c, the share of action a among the cell's completed runs.
- Decoding floor φ: φ_i = 1 − Σ_a p_FLOOR,i(a)², computed over item i's FLOOR runs. It is the probability that two runs on identical input disagree.
- JSD: the Jensen–Shannon divergence between a variant's action distribution and the item's BASE distribution, using log base 2 (bits).
- Control JSD: JSD(FLOOR, BASE). The text is identical, so this is pure sampling noise.
- Net JSD: JSD(variant, BASE) − JSD(FLOOR, BASE).
- TVD: ½ Σ_a |p_variant(a) − p_BASE(a)|.
- Net TVD: TVD(variant, BASE) − TVD(FLOOR, BASE). This is the materiality scale.
- Modal BASE action: the most frequent action among the item's BASE runs. Where two actions tie for most frequent, no mode is assigned and there is no tie-breaking.
- Modal flip rate: the share of a variant's runs whose action differs from the modal BASE action. It is secondary and governs no verdict. It is reported only for items whose BASE is not tied and whose φ < 0.20; otherwise the report prints the reason in place of the number.
- Baseline margin: the top-1 action share minus the top-2 action share among an item's BASE runs.

How cells are tested, corrected for multiplicity and aggregated is specified under Statistical models and Inference criteria.

---

## Analysis plan

### Statistical models

All inference is nonparametric and per engine. No parametric model (ANOVA, regression, SEM) is fitted. The scoring rules are implemented and pinned in scoring/, with a test suite that fails if any constant or procedure changes. The attached snapshot (scoring-snapshot-reg1-2026-08-16.zip, tag reg1-snapshot-2026-08-16) is authoritative, and this section describes it.

Unit of analysis. A cell is one item under one perturbation class on one engine. Each cell has an action distribution over {buy, sell, hold}.

Mapping of hypotheses to tests.

- H1 is tested on the N1 cells and H2 on the N3 cells, separately for each engine.
- H3, the attenuation ordering FinMem > FinAgent > TradingAgents, is a registered architectural prediction. It gets no inferential test. It is evaluated descriptively by comparing each engine's qualitative sensitivity verdict and magnitudes. Magnitude is only ever compared across engines with the attenuation stated alongside it, because φ-normalization corrects for decoding noise, not for how much weight the news channel carries. If the observed ordering violates the prediction, that is reported as a finding. If it matches, that is not reported as evidence of robustness.

Primary test: distributional shift. For each cell, the test statistic is the Jensen–Shannon divergence (JSD, in bits) between the variant's action distribution and the item's BASE distribution. It is reported net of the control JSD, which is JSD between BASE and FLOOR. JSD is primary at every φ because it doesn't require a stable modal action.

Significance. Each cell gets a permutation null built from that item's own pooled same-input draws (FLOOR + BASE):

- The pool is resampled with replacement into two independent samples matching the observed sample sizes.
- 10,000 resamples are drawn.
- p = (hits + 1) / (draws + 1), where a hit is a resampled JSD ≥ the observed JSD.

Because each null is built from the item's own floor pool, an item with high φ automatically gets a wider null and needs a larger shift to reach significance.

Multiplicity. The whole item × class grid for an engine is one family. Raw p, Benjamini–Hochberg-adjusted p and Holm-adjusted p are reported side by side:

- BH governs the read-out rule.
- Holm is reported for any cell quoted on its own.
- Raw p is never dropped.
- Cells whose p is undefined leave the family and are counted and named.

Intervals. Intervals come from a bootstrap over items, not runs: 10,000 draws, with φ recomputed on each resample. Resampling runs would treat repeats that share a headline, baseline and memory state as independent.

Seeds. There is one root seed. Every analysis stream is derived from it by name via SeedSequence, so any report can be reproduced from the logs plus the root seed.

Controls and checks.

- Negative control: BASE vs FLOOR. The text is identical, so any divergence between them is pure sampling noise, and every effect is reported net of it.
- Manipulation check: each engine's memory-reset mechanism is verified before its runs, and the verification is reported, so no run can remember a sibling variant.
- Fixture-quality check: directional shift, meaning the mean change in each action's share across items. A large, consistent direction is treated as a sign of drifted variants, not as a result.
- Version check: the scorer detects a split in backbone model version, and the affected rows are rerun.

Contingent analyses.

- An engine with median φ ≥ 0.50 is reported as decoding-unstable and carries no effect claim.
- Modal flip rate is reported for an item only when its BASE is not tied and φ < 0.20. Otherwise the report prints the reason in place of the number.
- FinAgent results are valid only under the price-frame condition in Study design: the substituted price frame ends at the decision date.

Subgroups and contrasts. Engines are analyzed separately. The contrasts are N1 vs BASE and N3 vs BASE within each item. There are no interactions or omnibus tests. The full rules are in the attached snapshot and readout-rule.md.

### Transformations

Actions are recorded as nominal categories {buy, sell, hold} and converted to within-cell proportions. They are not ordered, dummy-coded, centered or rescaled. JSD uses log base 2. φ = 1 − Σp² over each item's FLOOR actions. Net JSD and net TVD are formed by subtracting the BASE-vs-FLOOR control value. The modal BASE action is the most frequent BASE action. Where two actions tie for most frequent, no mode is assigned; there is no tie-breaking. Beyond these steps, no transformations are performed.

### Inference criteria

All criteria are fixed in the attached readout-rule.md. Filing this registration ratifies the four constants that document marks PROPOSED as the registered values.

Cell moved: a cell (one item under one perturbation class, within one engine) is declared moved when BH-adjusted p < 0.05 and net TVD ≥ 0.10. Both conditions are required, never either. Significance without materiality is a shift too small to matter; materiality without significance is noise at these run counts. TVD is the materiality scale because JSD is not linear in changes to action shares and depends on the baseline.

Engine verdicts, per engine and per class:

SENSITIVE TO REWORDING: at least 3 cells moved, spanning at least 2 distinct items.

STABLE: the upper bound of the 95% bootstrap CI on the class's net effect (net TVD) sits below the materiality threshold of 0.10, over at least 15 contributing items. STABLE is a claim about the perturbed channel, never about the agent. For FinAgent it is stated only as "stable to news rewording, visual channel held constant", never shortened to "stable".

NOT SHOWN TO BE SENSITIVE: the sensitivity criterion is not met, the stability test is not met, and the lower bound of the 95% bootstrap CI on the class's net effect (net TVD) is above 0. Some class-level effect is evident, but materiality is not established and too few cells moved to support an engine-level sensitivity claim. This is a weak result: it is consistent with a robust agent, an underpowered design, an attenuated channel or a fixture set that does not perturb much.

INCONCLUSIVE — underpowered: the sensitivity criterion is not met, the stability test is not met, and the lower bound of the 95% bootstrap CI on the class's net effect is at or below 0, so the data can neither establish an effect nor establish stability. The CI width and the number of contributing items are reported. The read-out rule states this outcome without a numeric boundary; this registration fixes it at the thresholds the rule already uses.

NOT SHOWN TO BE SENSITIVE and INCONCLUSIVE are mutually exclusive with each other and with the other two labels. If a class meets both the sensitivity and the stability criteria, both labels are reported together: a few items moved materially while the class-level net effect stays below the materiality threshold, which is the per-item spread the read-out rule treats as the statistic.

The engine-level label never replaces the per-cell table: the count and share of moved cells and the full per-cell spread are reported in every case.

Decoding-unstable: an engine with median φ ≥ 0.50 is reported as decoding-unstable and carries no effect claim.

Tails: the permutation test is one-sided in the upper tail. JSD is non-negative and undirected, so a change in the action distribution in any direction counts toward the upper tail. No directional hypothesis is tested.

Multiplicity: one family per engine over the whole item × class grid, corrected with Benjamini–Hochberg, with Holm reported alongside and raw p never dropped, as described under Statistical models.

Cross-engine: qualitative sensitivity verdicts are comparable across engines; magnitudes are not, because of attenuation (H3), and are compared only with the attenuation stated.

### Data inclusion and exclusion

All runs from the confirmatory matrix are included except in these cases:

- Rows with a status other than ok are excluded and counted by status.
- Rows produced under a superseded backbone model version are discarded and rerun.
- Rows whose frozen-context stamps differ are never pooled. The scorer refuses to pool them, which also mechanically excludes all rows from the 630-row fabricated-fixture pilot.
- An item with a tied BASE is excluded from flip-rate scoring only and kept in full for all distributional analysis.

There is no outlier removal. Actions are categorical, so outliers aren't defined. Nothing is capped or dropped silently: every exclusion is counted and named in the report.

### Missing data

Nothing is imputed. A cell that fails to produce runs is reported as missing, with its count, and is never silently dropped from a denominator. A cell with an undefined p leaves the multiplicity family and is named in the report. All other analyses use all available ok rows.

### Other planned analysis

These analyses are secondary and none of them governs a verdict:

- Modal flip rate: reported under the tie and φ < 0.20 gate, for legibility only.
- Directional shift: the fixture-quality alarm described above.
- Marginal action distribution: separates a stable agent from one that gives the same answer to everything.
- Baseline margin: top-1 share minus top-2, reported per item.

Declared sensitivity analyses vary --phi-interpretable-max, --null-draws and --seed, and are always reported alongside the registered value, never in place of it. Rationale text is recorded but has no registered confirmatory analysis, so any analysis of its content is exploratory. Anything else not specified here is exploratory and will be labelled that way.

---

## Other

### Context and additional information

Relation to a second registration. This registration fixes the design, variables, scoring rules and inference criteria. The confirmatory fixture set does not yet exist. Item count, repeats per cell and variants per class will be fixed in a separate Registration 2 at fixture freeze, before any confirmatory run. Any party executing this design may file Registration 2 in their own account, and nothing here commits any party to a date.

Attachments and provenance. Ten files are attached, bundled as reg1-attachments.zip with a SHA-256 manifest:

1. scoring-snapshot-reg1-2026-08-16.zip (the authoritative rules snapshot)
2. readout-rule.md
3. applicability-audit.md
4. applicability-matrix.json
5. candidate-scan.md (scouting-grade, labelled as such in its header)
6. worklog.md (provenance reconstruction, with evidence grades)
7. ai-disclosure.md
8. applicability-audit-material.md
9. applicability-matrix-material.json
10. citation-check-report.md

Attachments 1–7 are byte-identical to tag reg1-snapshot-2026-08-16 (commit 3f5be87). Attachments 8–10 postdate that tag and come from tag reg1-filing-2026-09b. The scoring rules froze at tag rules-registered-2026-08-09. One addition followed: total-variation distance (TVD), the materiality scale, which is pinned by its own tests and changes no frozen rule. Tags rules-registered-2026-08-09 and reg1-snapshot-2026-08-16 both predate any confirmatory run.

Ratification of the read-out rule. The attached read-out rule is filed unaltered, so it stays byte-identical to the snapshot. It therefore still carries its drafting header, which marks four constants as PROPOSED:

- the moved-cell criterion: BH-adjusted p < 0.05 and net TVD ≥ 0.10
- the sensitivity criterion: at least 3 cells moved, spanning at least 2 distinct items
- the stability criterion: the upper bound of the 95% CI below the materiality threshold across at least 15 items
- the decoding-instability threshold: median φ ≥ 0.50

Filing this registration ratifies those values as the registered values.

Material-class audit. A companion audit of five material perturbation classes is attached (attachments 8–9). This registration contains no material-class design. The audit is included for three reasons: it establishes the FinAgent price-frame condition, it records that class M4 has no target on any engine audited, and it shows what was known at filing. Any material-class confirmatory design would be a separate registration.

Reproducibility. Each engine is pinned by commit and never modified, and each arm runs in its own container. All arms share one copy of the scoring code, and every report prints the commit SHA it ran at. Every reported figure regenerates from the raw logs with one command. scripts/verify_citations.py checks every source citation in both applicability matrices against the pinned upstream clones, at the recorded pin; its report is attachment 10.

Known limitations, registered in advance:

1. Entity rename (N2) cannot be tested on any of the three engines. Each engine injects instrument identity outside the news text.

2. Attenuation confounds cross-engine magnitude (H3). Qualitative verdicts are comparable across engines; magnitudes are not.

3. FinAgent is multimodal, so a text-only perturbation exercises one of its two channels. The visual channel is held constant across cells. Separately, under the engine's base entry point the K-line image can carry post-decision price action. The registered price-frame condition closes this at the interception point, and FinAgent results are valid only under that condition. The issue was reported publicly upstream on 2025-04-14 (FinAgent issue #2) with no maintainer response, and this study's audit independently confirms it. Source reading alone cannot establish whether the upstream published experiments used the affected entry point, so no such claim is made.

4. A pilot on fabricated fixtures informed three analysis rules, as disclosed under Foreknowledge. No pilot row is pooled with confirmatory data.

5. One backbone model version per run matrix. Results do not generalize across backbones.

6. Dates in an author-controlled repository are a record, not proof. This OSF registration supplies the third-party timestamp that git history cannot.

7. Registrant position. The registrant develops an LLM-based trading-support system. The registered design, scoring rules and inference criteria are fixed in advance and apply identically regardless of outcome.
