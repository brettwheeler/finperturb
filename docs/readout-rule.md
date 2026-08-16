# The read-out rule

**Status: DRAFT for the project lead. Constants marked PROPOSED are the lead's
to set, and must be set before the registration snapshot and before any
confirmatory run.**

This is the rule that turns the report into a claim. It exists because
`score_pilot.py` deliberately reports and never concludes — there is no verdict,
no threshold and no pass/fail anywhere in it — which leaves the inference step
outside the code, where it can be fixed in advance or improvised afterwards.
This document is the "in advance".

A registration that says "the lead will decide" has a hole exactly where the
researcher degrees of freedom are. This closes it.

---

## 0. What is being claimed at all

The claim is about **one engine at a time**: *does this published agent change
its buy/sell/hold decision when a news item is reworded without changing its
meaning, beyond the rate at which it disagrees with itself on identical input?*

Everything below is per engine. Cross-engine comparison is secondary, confounded,
and governed by §6.

---

## 1. The unit of inference is the CELL

One cell = one item × one perturbation class, within one engine.

§7.5 of the build guide is explicit that the spread across items is the
statistic, not the mean — one item swinging hard is the finding, and averaging it
against nineteen quiet ones is how it gets lost. So the cell is primary and
aggregates are descriptive.

---

## 2. When a cell has MOVED

A cell is declared **moved** when **both** hold:

| criterion | measure | PROPOSED value |
|---|---|---|
| significance | Benjamini–Hochberg adjusted p, over the whole item × class family | **< 0.05** |
| materiality | net total-variation distance (TVD), variant vs base, minus the same-input control | **≥ 0.10** |

**Both, never either.** Significance without materiality is a large sample
detecting a shift too small to matter; materiality without significance is noise
at these run counts.

### Why TVD for materiality and not JSD

JSD is the right *significance* statistic — it needs no stable mode, so it
survives the high-φ items where a flip rate structurally cannot work. But it is a
poor *materiality* scale, because it is not linear in action-share change and
depends on the baseline. Computed with the registered code:

| change | JSD | TVD |
|---|---|---|
| unanimous baseline → 10-point shift | 0.0519 bits | 0.10 |
| 70/30 baseline → 10-point shift | **0.0079 bits** | 0.10 |
| 70/30 baseline → 20-point shift | 0.0303 bits | 0.20 |
| modal action flips (70/30 → 30/70) | 0.1187 bits | 0.40 |
| disjoint (all buy → all sell) | 1.0000 bits | 1.00 |

A single JSD threshold means a ~10-point shift on a unanimous item and a
~25-point shift on a 70/30 item. That would systematically under-flag movement on
unstable-baseline items — precisely the ones the study is most interested in.

TVD is baseline-independent and directly interpretable: **the share of runs that
would have to land on a different action to explain the shift.** TVD ≥ 0.10 means
at least a tenth of runs decided differently.

> **Code change made, 2026-08-09.** `scoring/divergence.py: total_variation`,
> reported per cell and per class net of the BASE-vs-FLOOR control exactly as
> JSD is; the worked table above is pinned verbatim in
> `scoring/test_scoring_rules.py`, so the document and the code cannot disagree
> about what 0.10 means without a test failing. It was an addition, not a change
> to any registered rule — but the `scoring/` snapshot attached to Registration
> 1 must be **re-tagged**, because `rules-registered-2026-08-09` predates it.

### φ needs no separate exclusion here, and that is not an oversight

A high-φ item does not need screening out of the JSD analysis, because the
permutation null is built from **that item's own same-input pool**. An item that
disagrees with itself constantly produces a wide null automatically, so a larger
observed divergence is required to reach significance. The instrument
self-corrects for decoding noise. (The *flip rate* has no such property, which is
why it alone carries the φ < 0.20 interpretability gate.)

---

## 3. When an ENGINE is declared sensitive

Per engine, per class, over that engine's runnable cells:

- **SENSITIVE TO REWORDING** — **PROPOSED: ≥ 3 cells moved, spanning ≥ 2 distinct
  items.** Three because BH at q = 0.05 expects roughly one false discovery in
  twenty declarations, so a single moved cell is within what the procedure
  permits. Two distinct items because one pathological item can move under both
  classes and should not, by itself, carry an engine-level claim.
- **NOT SHOWN TO BE SENSITIVE** — fewer than that, and §4's stability test not met.
- **STABLE** — §4.

Report the count and share of moved cells and the full per-cell spread in every
case. The engine-level label never replaces the table.

---

## 4. When an engine is declared STABLE — the claim that needs the most care

`score_pilot.py`'s own context-stamp comment already draws this distinction:
*"no evidence of a mismatch" and "evidence of no mismatch" are not the same
claim*. The same rule governs here.

Not finding movement is **NOT SHOWN TO BE SENSITIVE**. That is the default null
result and it is weak — it is consistent with a robust agent, an underpowered
design, an attenuated channel (§6) or a fixture set that does not perturb much.

**STABLE** is a positive claim and requires an equivalence test:
**PROPOSED: the upper bound of the 95% bootstrap CI on that class's net effect
sits below the materiality threshold (TVD 0.10), over ≥ 15 contributing items.**
That is "we can rule out an effect big enough to matter", which is a different
and much stronger statement than "we did not detect one".

If the CI is too wide to do either, that is the honest outcome and is reported as
**INCONCLUSIVE — underpowered**, with the CI width given.

**STABLE is always a claim about the perturbed channel, never about the agent** —
every engine's decision also rests on channels the study deliberately holds
fixed (prices, indicators, memory state), and an equivalence test on the news
channel says nothing about them. For most engines the frozen-context framing
carries that scoping. **For FinAgent it must be carried by name**: that engine
sends the backbone chart images (the applicability audit's scope finding), and
the image reaches the model *more directly than the news does* — the news
crosses a ≤300-token LLM summary, the image is passed intact. The unperturbed
channel is the less-attenuated and plausibly higher-weight one, so the strongest
claim a passing equivalence test can license for FinAgent is **"stable to news
rewording, visual channel held constant"** — in those words, never shortened to
"stable". This is a distinct ground from §6's attenuation confound and the two
are stated separately when reporting.

---

## 5. When an engine cannot be measured at all

**PROPOSED: if the median per-item φ for an engine is ≥ 0.50**, the engine is
reported as **DECODING-UNSTABLE: perturbation effects are not separable from
self-disagreement at this run count.**

This is a finding, not a failure, and it is arguably the more newsworthy one — an
agent that disagrees with itself on identical input half the time has a
robustness problem that no rewording is needed to expose. It is reported with the
φ distribution and without any effect claim.

---

## 6. Cross-engine comparison — pre-declared as confounded

The applicability audit established, from source and before any data, that the
engines dilute the perturbed channel to different degrees:

```
FinMem          news -> prompt, verbatim                     0 lossy stages
FinAgent        news -> LLM summary, <=300 tokens            1 severe stage
TradingAgents   news -> analyst report -> debate, 1 of 5     2 stages + channel share
```

Therefore, **registered in advance**:

1. The **predicted** ordering of effect magnitude is FinMem > FinAgent >
   TradingAgents, on architecture alone.
2. Observing that ordering is **not evidence** that TradingAgents is more robust.
   It is what the architecture predicts, and it will be reported as such.
3. Observing the ordering **violated** — e.g. TradingAgents moving more than
   FinMem — is a genuine finding and is reported as one.
4. Magnitude is compared across engines **only** with the attenuation stated in
   the same sentence. φ-normalization does not fix this: φ normalizes decoding
   noise, not channel weight.
5. The **qualitative** claim ("this engine is / is not sensitive") is comparable
   across engines. The magnitude is not.
6. Attenuation has two components, and a report states both rather than folding
   them into one "lossy stages" count: **transformation** (stages that rewrite
   the news — a summary, an analyst report, a debate) and **dilution** (the news
   being one of several parallel decision channels — four unperturbed analyst
   reports in TradingAgents, an entire unperturbed image channel in FinAgent).
   The candidate scan (`docs/candidate-scan.md`) found the two axes fully
   independent in the field — an engine can pass news verbatim, zero lossy
   stages, and still drown it among independently-fetched channels — so neither
   number substitutes for the other.
7. **For FinAgent, the unperturbed channel is the less-attenuated one.**
   The chart image is passed to the backbone intact while the news crosses a
   severe summarization stage. Registered here, in advance, so that a null on
   FinAgent's news channel is read at its actual weight — and so §4's scoping
   of any FinAgent stability claim is recognisable as pre-declared rather than
   post-hoc.

---

## 7. N2 across all three engines

The audit dropped N2 on all three, each for a deliberate independent
identity-injection in the engine's own prompt construction. This is reported as a
**general finding** — the rename class is not testable against agents that anchor
instrument identity outside the news text, which is all three — and never as a
per-engine caveat or an omission.

No N2 number will be reported for any engine, including any that a future
harness could technically produce.

---

## 8. What is never claimed, whatever the numbers

- **No claim about trading profitability.** The study measures decision
  stability. A stable agent is not thereby a good one, and an unstable one is not
  thereby unprofitable.
- **No claim that a moved cell is an error.** The correct decision on the reworded
  item is unknown; the study measures *change*, not *correctness*.
- **No ranking of engines by quality**, for §6's reasons.
- **No generalization beyond** the engines, the backbone model version, the
  frozen contexts and the fixture set actually run.
- **No claim from the pilot.** The 2026-08-09 rehearsal used fabricated fixtures
  and hand-written unaudited variants. It is reported as instrument development
  and never pooled with confirmatory rows — enforced mechanically by the context
  stamp, which makes the scorer refuse to pool differing contexts.

---

## 9. Analysis discipline

- The scorer runs **once**, on the complete matrix. No interim analysis, no
  stopping early, no re-running with different constants and choosing.
- Any run of the scorer against partial confirmatory data is operational (is the
  harness working) and its numbers are not used for any decision. Say so in the
  log.
- `--phi-interpretable-max`, `--null-draws` and `--seed` exist for declared
  sensitivity analyses only. A sensitivity analysis is reported **alongside** the
  registered value, never in place of it.
- Every exclusion is counted and named in the report. No silent caps.

---

## 10. What would surprise us

Stated in advance so that a surprising result is recognisable as one rather than
rationalised afterwards:

- **A large N3 effect.** An appended irrelevant sentence changing decisions is a
  stronger result than a paraphrase doing so, because the semantic content is
  untouched by construction. On FinAgent it would be stronger still, since that
  engine is explicitly instructed to disregard unrelated market intelligence.
- **A moved cell on FinAgent at all.** Its news channel crosses the severest
  single summarization stage in the study, and its decision also leans on an
  unperturbed image channel that reaches the backbone more directly (§6.7).
  Rewording that survives both — moving the decision through a ≤300-token
  summary while the chart holds still — is close to the strongest single-engine
  result this design can produce.
- **The attenuation ordering violated** (§6.3).
- **A consistent DIRECTION across items** — the existing directional-shift
  diagnostic. Instability is directionless; a consistent push toward buy or sell
  points at the variants rather than the agent and is read as a **fixture-quality
  alarm**, not a finding. This is exactly what it caught in the pilot
  (+0.317 toward buy on hand-written paraphrases).
- **φ higher than the perturbation effect on most items** — the agent's
  self-disagreement dominating anything rewording does, which would make the
  headline finding "these agents are unstable full stop" rather than "these
  agents are sensitive to rewording".
