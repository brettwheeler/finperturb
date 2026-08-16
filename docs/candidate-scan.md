# Candidate-engine scan — engines NOT in the study

**Scanned 2026-08-09.** Diagnostic only. These engines — CryptoTrade,
FinRobot, StockAgent (and QuantAgent/Xiong, added below) — are **not** subjects
of the paper; the study stays at the three pinned arms (FinMem, TradingAgents,
FinAgent). The purpose of the scan was narrow: run the item-3 applicability
protocol against more published agents to see whether either of two things
happens — (a) they change the **injection shape** (the N1/N2/N3
RUN/ATTENUATED/DROPPED story), or (b) they surface a new finding of the kind
FinAgent's visual channel was.

> **PROVENANCE — read before citing any line below.** Unlike the three subject
> engines, these three were read at **branch HEAD, not a pinned SHA**, via raw
> file reads, and the line numbers are **approximate (±a few lines)**. The
> *relational* facts (what enters the decision, what is hardcoded, whether any
> image channel exists) are confirmed from source strings; the *coordinates* are
> not provenance-grade. Nothing here is citable in the paper until the engine is
> pinned and re-read against a fixed SHA. This memo is a scouting report, not an
> audit of record.

---

## The matrix — candidates beside the subjects

| class | FinMem `be814aa` | TradingAgents `a33fd4c` | FinAgent `17248a0` | CryptoTrade *(HEAD)* | FinRobot *(HEAD)* | StockAgent *(HEAD)* | QuantAgent/Xiong `00a88cb` |
|---|---|---|---|---|---|---|---|
| **N1** paraphrase | RUN | RUN, ATTEN ×2 | RUN, ATTEN (severe) | RUN, ATTEN (1) | **RUN** | RUN, ATTEN (dual-ch) | **N/A — no news channel** |
| **N2** rename | DROPPED | DROPPED | DROPPED | **DROPPED** | **DROPPED** | DROPPED / ill-defined | N/A — no news channel |
| **N3** no-op append | RUN | RUN, ATTEN ×2 | RUN, ATTEN | RUN, ATTEN (1) | **RUN** | marginal | N/A — no news channel |
| lossy stages (news→decision) | 0 | 2 | 1 | 1 | **0** | dual-channel | — |
| decision modality | text | text | **image + text** | text (multi-ch) | text (multi-ch) | text (multi-ch) | **image + text** |

The injection shape does **not** change. Every candidate with a news channel
lands in the same three-verdict frame the subjects did, for the same structural
reasons — and QuantAgent/Xiong establishes the fourth possible outcome the frame
needed: **N/A, the engine has no news channel at all** (price-only by
construction, as its title claims). That is the news-absent endpoint of the
channel spectrum, not a counter-example to anything.

---

## CryptoTrade — reflective single-agent, ETH/BTC/SOL

- **Interception point** (if it were ever run): patch the per-day news JSON in
  `{news_dir}/{YYYY-MM-DD}.json` — a data-pipeline substitution, the FinAgent
  pattern, not a tool-vendor registration.
- **N1 / N3 — RUN, ATTENUATED (1 stage).** News enters `state['news']`
  (`eth_env.py`) and is embedded verbatim into the news-analyst prompt
  (`env_history.py get_prompt` ~L45), but the **trader LLM never sees raw news** —
  it sees the news analyst's "one concise paragraph" (`eth_trial.py` ~L53→L62).
  One summarization stage, same tier as FinAgent. N3 is the most attenuated of the
  three, because "write one concise paragraph … estimate the market trend" is
  precisely the instruction that discards an appended no-op.
- **N2 — DROPPED.** The asset string `"ETH"` is a **hardcoded literal** in the
  analyst and trader templates (`env_history.py` ~L43, L55), and the traded asset
  is fixed by `args.dataset` selecting the price/on-chain CSVs. Identity enters
  from template/config, never from the news. Canonical drop.
- **Modality — multi-channel, TEXT-ONLY.** Three channels fused in the trader
  prompt: a structured numeric channel (price + MACD/Bollinger/SMA + on-chain
  metrics) → on-chain analyst (always on, heavy weight); the news channel (gated
  by `use_news`); a reflection channel. The numeric channel is text-serialized
  numbers, **not** an image. `utils.py get_chat()` sends plain-text content only —
  no `image_url`, no base64.

## FinRobot — multi-agent platform; FinGPT-Forecaster workflow

- **Workflow audited:** the `SingleAssistant` "Market_Analyst" / FinGPT-Forecaster
  (`tutorials_beginner/agent_fingpt_forecaster.ipynb`) — its only news→directional-
  call analogue. Other workflows (annual-report, RAG QA, equity debate) are not
  news→decision and were not scanned.
- **Interception point:** fixture the `get_company_news` tool return — a
  tool-vendor substitution, the TradingAgents pattern.
- **N1 / N3 — RUN. Zero lossy stages.** `get_company_news`
  (`finrobot/data_source/finnhub_utils.py` ~L47) passes the Finnhub
  `{headline, summary}` through **raw**, delivered as a tool-return message
  straight into the single deciding agent. No summary, report, or debate
  intervenes. This is a **second 0-stage engine**, tying FinMem for directness on
  the news text itself.
- **N2 — DROPPED.** `get_company_profile` (~L33–44) injects
  `"{name} … in the {finnhubIndustry} sector … trading under the ticker {ticker}
  on the {exchange}"` from a Finnhub lookup on the **real symbol**, independent of
  the news; `get_basic_financials` and `get_stock_data` also fetch by real ticker.
  Rename the company in the news and the profile/price/financials channels
  contradict it. Canonical drop.
- **Modality — multi-channel, TEXT-ONLY.** Four channels, all text/JSON/table:
  news, company profile (the N2 injector), basic financials, price history. No
  image in this workflow. (A separate `ollama stock chart` tutorial renders charts;
  different workflow, not this decision path.)

## StockAgent — event-driven multi-agent market simulation

- **FIT: related work, not a subject.** It studies emergent behaviour in a
  simulated order-book market, not a news→buy/sell/hold pipeline. Confirmed from
  source, three ways:
  1. **"News" is a fixed enumerated set of two scripted macro shocks**
     (`main.py` ~L104–109), selected by hardcoded date, not authored per-step
     prose. Each shock injects a free-text `EVENT_x_MESSAGE` into the forum **and**
     independently mutates a numeric `LOAN_RATE` on the same line — the causal
     channel is the number, not the sentence.
  2. **Assets are fictional labels** ("A"/"B"/…), identity injected structurally
     via `Stock` objects and name-keyed prices/holdings. N2 (rename) is
     ill-defined — there is no real ticker or company-tied news to rename.
  3. Prices form endogenously from the order book; agents react to each other's
     forum posts. Text-only; no image channel; no real tickers.
- Net: N1 attenuated-and-marginal (two events, dual-channel), N2 ill-defined, N3
  marginal. Cite as related work on LLM market simulation, not as a subject.

---

## What the scan changes — two upgrades and one reframe

### 1. N2 is now dead 6-for-6, not 3-for-3 — upgrade the general finding

Every candidate drops N2 by the same mechanism the subjects do: instrument
identity injected independently of the news — hardcoded `"ETH"` (CryptoTrade), a
Finnhub profile lookup on the real symbol (FinRobot), structural fictional labels
(StockAgent). Zero counter-examples in six engines spanning single-agent
reflection, a multi-agent platform, and a market simulation.

This strengthens `readout-rule.md §7` and `cross_cutting.n2_universally_dropped`
from "all three subjects" to "**every deployed LLM trading agent we examined,
across three architectural genres.**" (QuantAgent/Xiong, audited below, neither
extends nor breaks the count — it has no news channel for N2 to act on — but its
config-side `stock_name` injection makes the *mechanism* 7-for-7: every engine
examined anchors instrument identity outside the perturbable text.) The claim that a whole category of
surface-form robustness test is unavailable against this class of system is no
longer resting on the three engines the study happened to pick. Worth a sentence
in the paper to that effect — with the provenance caveat that the three extra
engines were scouted, not pinned-and-audited.

### 2. Attenuation spans 0–2 stages across the field, and there is a sub-type worth naming

FinRobot is a **second 0-stage engine** (news passed verbatim to the deciding
agent) that is nonetheless **heavily diluted** — the news competes with three
other independently-fetched channels (profile, financials, price). So "0 lossy
stages" and "low channel weight" are **independent axes**. The §6 attenuation
story currently conflates them under "lossy stages"; the field data says separate
them: *transformation attenuation* (summaries, reports, debate — FinAgent,
TradingAgents, CryptoTrade) versus *dilution attenuation* (news is a minority
input among parallel channels — FinRobot, CryptoTrade, StockAgent, and again
FinAgent/TradingAgents). Most engines have both.

### 3. The visual channel — answering the actual question

The scan was the way to learn whether "trading agents consume a visual channel,
not just text" is a **FinAgent quirk or a field-wide class**. The answer is
specific:

- **As literal images: n = 2 of the seven engines examined.** FinAgent (2024)
  sends base64 K-line charts as `image_url`; **QuantAgent/Xiong (2025), audited
  below, is a confirmed second member** — mplfinance-rendered candlestick and
  trendline charts, base64 PNG via `image_url`, consumed by two dedicated vision
  agents. CryptoTrade, FinRobot's forecaster, and StockAgent are text-only. Two
  engines is not yet a field norm, but the second member is the *newer* system,
  and its entire perception layer is chart-reading — consistent with the image
  channel being an emerging pattern rather than a one-engine quirk. The n=1
  claim in earlier drafts of this memo is superseded.

- **As the underlying property — the perturbed news channel is a minority
  shareholder of a multi-channel decision — the class is 6-for-6.** Every engine
  fuses news with other decision-weighted channels the study holds fixed:
  FinAgent's chart image is the *extreme* end of a spectrum, not a category of its
  own. The spectrum:

  ```
  news absent entirely — nothing to perturb            QuantAgent/Xiong
  image, a modality text tools cannot perturb at all   FinAgent, QuantAgent/Xiong
  independent numeric market/on-chain series           CryptoTrade, FinRobot, StockAgent
  four-of-five unperturbed analyst reports             TradingAgents
  ```

This is the correct generalization, and it is a **better** finding than "some
agents have charts." It says: **in every engine examined, a news-only perturbation
moves one channel of a structurally multi-channel decision.** That is the honest,
universal scope of the whole study — not a FinAgent footnote.

---

## So: are we testing the whole engine, and do we need the visuals?

Split the claim in two; the answer differs by which one.

- **The registered claim** (`readout-rule.md §0`): *does this engine change its
  decision when the **news** is reworded, net of the decoding floor?* That claim
  is about the news channel. Holding every other channel fixed — the chart, the
  price series, the financials — is not a gap; it is the **control**. For this
  claim you are testing the engine correctly, and you need neither to perturb nor
  to display the visuals. This is true for all six engines, because all six are
  multi-channel; FinAgent is not special here, only sharper.

- **The whole-agent claim** ("this engine is robust / stable"): here the held-fixed
  channels bite, **asymmetrically**. A **moved** cell survives — rewording news
  alone flipped the decision despite fixed charts/prices, a real finding. A
  **null** cell cannot license STABLE, because the decision also rests on channels
  the perturbation never touched, and — the sharp part — in FinAgent the untouched
  **image** channel is passed to the model *more directly than the news*, which
  goes through a ≤300-token summary first. **The channel you are not testing is the
  less-attenuated, higher-weight one.** A text-only null there is doubly weak:
  attenuated tested channel, untested dominant channel.

**Recommendation — keep the study; scope the claim; two small edits; one figure.**

1. **Keep** the three-engine, news-channel, within-engine design. Do **not**
   silently add a visual perturbation class — that is a different, bigger paper
   (see below).
2. **`readout-rule.md §4`:** make STABLE explicitly **unavailable** for any engine
   with an unperturbed non-text decision channel — FinAgent named — or restrict it
   at most to "stable to news rewording, visual channel held fixed." Today §4/§8
   forbid over-generalization on *attenuation* grounds; add the *held-fixed-channel*
   ground by name.
3. **`readout-rule.md §6 / §10`:** register, in advance, "the untested channel may
   be the less-attenuated, higher-weight one (FinAgent: image passed direct vs
   news summarized to ≤300 tokens)" as a limitation and a surprise-worthy point;
   and split *transformation* vs *dilution* attenuation per finding 2 above.
4. **One figure**, not a class: show a single K-line image FinAgent actually
   receives. It is evidence for the scope finding, makes the two-channel claim
   checkable, and is the agent's own input (not third-party copyrighted content).

**The other paper (explicitly out of scope here).** Perturbing the *non-news*
channels — a meaning-preserving chart re-render for FinAgent (same OHLC, different
palette/DPI/gridlines/library), or a value-preserving reformat of the numeric
channel for CryptoTrade/FinRobot — is the study that tests the *whole* engine.
Note the likely verdict for FinAgent's chart re-render is **RUN, 0 stages** (the
image is passed intact), so the visual channel is *more* testable than the news
channel — which is exactly why it is a real contribution and a real second study,
not an add-on to this one. Flag as future work; do not let it expand the current
matrix.

---

## "QuantAgent" — a name collision the paper and protocol must disambiguate

There are **two unrelated systems named QuantAgent**, and the one in the
reference list is not the one with code:

| | Wang et al. 2024 | Xiong et al. 2025 |
|---|---|---|
| arXiv | 2402.03755 | 2509.09995 |
| system | self-improving **alpha-miner** loop | **price-driven multi-agent HFT**, chart-reading |
| code | **none found** (as of 2026-08; appears never open-sourced) | **Y-Research-SBU/QuantHarness** (MIT, active) — the repo was **renamed** from `…/QuantAgent`; the old URL redirects | 
| status here | reference list #5 — related work, cited for the alpha-miner class | scan candidate, audited below |

The rename (observed 2026-08-09; GitHub API `full_name` now `QuantHarness`,
plausibly to shed the brand collision) cuts both ways: it reduces future
confusion, but any citation of the Xiong repo must give **both** names, since
the paper says "QuantAgent" and the code now says "QuantHarness".

Rules, for the paper and every draft after it:

1. **Do not swap the citation.** Reference #5 is cited for alpha-miner claims;
   Xiong 2025 is a different architectural genus and cannot back them. If Xiong
   2025 earns a citation, it earns its **own** entry (most likely as evidence
   that the image channel is spreading in newer systems), never as a substitute.
2. **Disambiguate by arXiv ID at first mention** — "QuantAgent (Wang et al.
   2024, arXiv:2402.03755; not to be confused with the unrelated QuantAgent of
   Xiong et al. 2025, arXiv:2509.09995)" — because a reader who searches the
   name finds Xiong's active repo and will otherwise conclude the paper
   misdescribes the system it cites.
3. **Date the no-code claim** — "no public implementation located as of
   2026-08" — repos sometimes appear years after the paper.
4. Wang et al.'s missing code is also a **datum**: the subject population of
   this study is not "published LLM trading agents" but "published agents with
   released code," and QuantAgent (Wang) is a named instance of the gap between
   those two sets. State the selection effect once, in the paper.

### QuantAgent (Xiong 2025) — audit

**Read at `main` @ `00a88cb` (2026-07-24), raw-file reads; approximate line
numbers, scouting-grade like the three scans above — but note this one *was*
read at a recorded commit.**

- **No news channel exists — N1/N2/N3 all N/A.** Definitive from the closed
  LangGraph state schema (`StateGraph(IndicatorAgentState)`, `graph_setup.py`):
  no field in `agent_state.py` carries free text from outside. The only external
  inputs anywhere are asset code, timeframe, and yfinance OHLCV. The engine is
  price-only by construction, exactly as its title claims.
- **Confirmed multimodal — the second image-sending engine.** `graph_util.py`
  renders candlestick charts (last 40 candles) and trendline-annotated charts
  (last 50, computed support/resistance overlaid) with mplfinance, base64 PNG →
  `image_url` in a `HumanMessage` (`pattern_agent.py`, `trend_agent.py`). Two
  dedicated vision agents judge classical patterns and trend direction from the
  image. The Indicator and Decision agents are text-only.
- **Architecture:** strict linear pipeline, Indicator → Pattern → Trend →
  Decision. Each raw channel passes through exactly **one** analyst-report
  stage; the decision LLM never sees raw prices or images. Decision space is
  **LONG/SHORT only — HOLD prohibited** ("HFT constraints"), a different action
  space from buy/sell/hold.
- **Identity injection: present, 7-for-7 as a mechanism.** `stock_name` enters
  the Decision prompt from config (`asset_mapping`, `web_interface.py`),
  independent of every data channel — the same mechanism that drops N2
  everywhere else. Notably the three analyst agents are **identity-blind** (no
  ticker in their prompts; charts and kline JSON carry no name).
- **Fit:** not a subject for this study (nothing to perturb). **Strong candidate
  for the channel-weight second study**, for three reasons: (a) the image and
  text channels are rendered deterministically from the *same* OHLC, enabling
  perturb-one-hold-the-other cross-modal designs; (b) `web_interface.py`
  pre-seeds images into initial state, a ready-made injection point requiring
  zero agent-code changes; (c) the forced LONG/SHORT binary gives a crisp flip
  metric with no HOLD absorbing state. Its identity-blind analysts also make it
  an unusually clean probe of pure identity-sensitivity (rename via config,
  nothing downstream contradicts it) — the exact probe N2 could not be on
  news-bearing engines.
