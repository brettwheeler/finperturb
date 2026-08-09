# Perturbation-applicability audit — three engines

**Audited 2026-08-09** against pinned source. No engine was run; this is entirely
source reading, which is the point — the finding that killed N2 for FinMem came
from reading `prompts.py:16`, not from a result.

| engine | pin | audited paths |
|---|---|---|
| FinMem | `be814aa` | `puppy/prompts.py`, `puppy/reflection.py`, `puppy/memorydb.py`, `puppy/embedding.py` |
| TradingAgents | `a33fd4c` | `agents/analysts/*.py`, `agents/utils/agent_utils.py`, `agents/utils/news_data_tools.py`, `dataflows/interface.py` |
| FinAgent | `17248a0` | `res/prompts/module/trading/*.html`, `res/prompts/asset_infos/*.json`, `finagent/provider/provider.py` |

## The protocol

Before any confirmatory run on an engine, read its prompt-construction path and
record, **per perturbation class**, whether the perturbation survives into the
prompt the decision is made from, or is contradicted, erased or diluted
downstream of the fixture text. A class that fails is **dropped for that engine
with the reason logged**; the drop is enforced in that arm's
`harness/corpus_config.json` (`excluded_klasses`, and the builder refuses to run
if a class is excluded without a stated reason), counted in the corpus manifest,
and printed in the report.

Three verdicts, and the middle one is the one that is easy to miss:

- **RUN** — the perturbation reaches the decision prompt intact.
- **RUN, ATTENUATED** — it reaches the decision, but through a lossy stage
  (LLM summarization, a report, a debate). Valid, but the effect size is not
  comparable across engines without saying so. **This is not a drop.**
- **DROPPED** — the perturbation is contradicted or erased downstream. Measuring
  it would measure the contradiction, not sensitivity to surface form.

## The matrix

| class | FinMem `be814aa` | TradingAgents `a33fd4c` | FinAgent `17248a0` |
|---|---|---|---|
| **N1** paraphrase | **RUN** | **RUN, ATTENUATED** ×2 | **RUN, ATTENUATED** (severe) |
| **N2** rename | **DROPPED** — ticker injected | **DROPPED** — ticker + company name + sector | **DROPPED** — full profile, *and erased by instruction* |
| **N3** no-op append | **RUN** | **RUN, ATTENUATED** ×2 | **RUN, ATTENUATED** + explicitly defended |

Interception point differs per engine and is not a detail — it is where each
harness must inject fixtures:

| engine | where the news text enters | interception |
|---|---|---|
| FinMem | memory rows, verbatim into the prompt | memory injection (current harness) |
| TradingAgents | **a tool call**, not a prompt input | register a fixture vendor in `VENDOR_METHODS` |
| FinAgent | a data pipeline (`tools/download_news.py`) | substitute the processed data |

---

## FinMem — `be814aa`

**N1 paraphrase — RUN.** News text enters as `short_memory` rows and is joined
into `investment_info` verbatim, with only `.strip()`
(`puppy/reflection.py:325`). No summarization stage. No truncation: `top_k`
bounds the *number* of memories (`memorydb.py:147-148`), and the embedder chunks
at 5,000 tokens and **averages** rather than truncating (`embedding.py:10-11`).

One property worth stating rather than treating as a flaw: the text is embedded
for retrieval, so a paraphrase can change *which* memories are retrieved. That
is the agent's own behaviour and part of what the study measures — it is not a
contradiction introduced downstream.

**N2 rename — DROPPED.**
`test_investment_info_prefix = "The ticker of the stock to be analyzed is
{symbol} and the current date is {cur_date}"` (`prompts.py:16`), formatted from
config at `reflection.py:319-321`, independent of the news. An N2 variant yields
a prompt naming TSLA in its header and "Company A" in its body — a
self-contradictory prompt, not a meaning-preserving rewrite. §4.3's audit cannot
see it, because the reviewer compares two texts and the contradiction is
introduced downstream by the agent's own prompt assembly.

**N3 no-op append — RUN.** Same verbatim path as N1.

**Out of scope but recorded:** `_add_momentum_info` (`reflection.py:227-243`)
injects price direction as independent English text. Any future price-context
perturbation class would fail here for the same reason N2 does.

---

## TradingAgents — `a33fd4c`

**The architecture is different in kind, and it changes the harness before it
changes the verdicts.** The news is **not a prompt input**. The news analyst is
given tools and fetches it: `get_news(ticker, start_date, end_date)`
(`analysts/news_analyst.py:20-28`), which resolves through
`route_to_vendor("get_news", ...)` (`agents/utils/news_data_tools.py:24`).

That is good news for feasibility: `VENDOR_METHODS` is a registry
(`dataflows/interface.py:168-198`) and the vendor chain is configuration
(`default_config.py:133`), so a fixture vendor can be **registered** rather than
monkeypatched. The engine stays unmodified.

**N1 / N3 — RUN, ATTENUATED, twice over.** Two dilution stages sit between the
fixture and the decision, and neither exists in FinMem:

1. The news analyst LLM does not pass the news through — it **writes a report**
   (`news_analyst.py:59-67`). The raw text never reaches the decision.
2. The decision is a **debate over five analyst reports** — news, market,
   fundamentals, sentiment, social — through bull/bear researchers, a research
   manager, a trader, a risk debate and a portfolio manager. Four of the five
   inputs are unperturbed by construction.

**N2 rename — DROPPED, more decisively than FinMem.**
`build_instrument_context` (`agent_utils.py:122-157`) injects the ticker, the
**company name**, business classification (sector / industry) and exchange,
resolved by live identity lookup, under the instruction *"Use this exact ticker
in every tool call, report, and recommendation."* It is re-injected between
analysts by `create_msg_delete` (`agent_utils.py:204-211`). The docstring cites
upstream issue #814: anchoring to the real company is a deliberate design goal,
not an oversight.

---

## FinAgent — `17248a0`

**N1 — RUN, SEVERELY ATTENUATED.** News passes through the market-intelligence
module, where an LLM compresses it to **≤40 tokens per item** and a **≤300 token
summary** before anything reaches the decision
(`market_intelligence_latest_summary_prompt_trading.html`). The decision never
sees the fixture text.

**N2 rename — DROPPED, and by two independent mechanisms.** This is the most
decisive of the three:

1. **A full company profile is injected**, in both the decision and
   market-intelligence task descriptions: `$$asset_name$$`, `$$asset_symbol$$`,
   `$$asset_exchange$$`, `$$asset_sector$$`, `$$asset_industry$$` and
   `$$asset_description$$` (`decision_task_description_trading.html`,
   `market_intelligence_task_description_trading.html`), populated from the
   static `res/prompts/asset_infos/exp_stocks.json` — which carries
   `companyName: "Apple Inc."`, exchange, sector, industry and a business
   description.
2. **The model is instructed to erase the name**: *"It should NOT contain IDs,
   $$asset_name$$ or $$asset_symbol$$"* — twice, for both the per-item analysis
   and the retrieval query. So a rename is not merely contradicted, it is
   **deliberately stripped** before reaching the decision. That is a distinct
   failure mode from FinMem's: **erasure**, not contradiction.

**N3 — RUN, but explicitly defended against, with a strong null prior.** The
market-intelligence prompt's first rule is literally *"Please disregard
UNRELATED market intelligence."* The appended irrelevant sentence is the exact
thing that instruction targets. This remains a **valid** test — a decision
change under it would be *more* interesting, not less — but a null result here
must be read as "the filter worked," not as general robustness.

**SCOPE FINDING — the engine is multimodal, and the study is text-only.**
Confirmed at source: base64 JPEG payloads are sent as `image_url` content
(`finagent/provider/provider.py:270-284`, `411-444`), carrying K-line charts
with moving-average and Bollinger-band overlays
(`low_level_reflection_kline_chart_trading.html`). A text-only perturbation
measures **one channel of a two-channel agent**. This is a limit on what a φ or
JSD figure from this engine means, and it must be registered as one — with the
visual channel held constant across all cells stated explicitly as a design
condition, not left implicit.

---

## Two cross-cutting findings

### 1. N2 is dead on all three engines, and that is a result, not a limitation

Every engine audited injects instrument identity independently of the news, and
each does so **deliberately** — FinMem to scope memory and portfolio,
TradingAgents to stop the agent pattern-matching to the wrong company (#814),
FinAgent to give the analyst a business profile. The reason is structural:
an agent that calls tools by ticker and retrieves memory by symbol must anchor
identity outside the text.

So the rename perturbation is **not testable on this class of system without
modifying the agent**, which the study forbids. That converts "N2 dropped for
FinMem" from a local caveat into a general finding worth reporting: a whole
category of surface-form robustness test is unavailable against deployed
LLM trading agents, and any future work proposing it needs to say how it
handles independent identity injection.

### 2. Attenuation is monotone across the three, and it confounds cross-engine comparison

Architecture alone predicts the effect-size ordering, before any data:

```
FinMem          news -> prompt, verbatim                      (0 lossy stages)
TradingAgents   news -> LLM report -> debate, 1 of 5 inputs   (2 lossy stages)
FinAgent        news -> LLM summary, <=300 tokens             (1 severe stage)
```

**This is the biggest threat to the study's headline comparison.** A naive
reading of smaller effects on TradingAgents as "TradingAgents is more robust"
would be wrong — the news channel there is one-fifth of the input and twice
summarized. The engines differ in *channel weight*, and φ-normalization does not
correct for that, because φ measures decoding noise rather than how much of the
decision the perturbed channel drives.

Consequences, all of which are registration content:

- Register the ordering **as a prediction**, now, before the runs. If observed
  effects come out in this order, that is architecture, not robustness; if they
  come out against it, that is a genuine finding.
- Report per-engine effects primarily **within engine** (does rewording move
  this agent?), and treat cross-engine magnitude comparison as secondary and
  explicitly confounded.
- Consider publishing a per-engine **news-channel share** descriptor so a reader
  can see the denominator rather than infer it.
