# Perturbation-applicability audit — material classes, three engines

**Audited 2026-09-15** against pinned source. No engine was run; this is entirely
source reading, in the same discipline as the null-class audit
(`docs/applicability-audit.md`, 2026-08-09), whose mechanisms this document cites
rather than restates. The material classes M1–M5 had never been audited; they
were about to be published as specification. That would have repeated, inside the
paper that reports the N2 finding, the error the N2 finding names: a perturbation
class tests only what traverses the channel it perturbs, and agent scaffolds route
decision-relevant content around that channel.

| engine | pin | audited paths |
|---|---|---|
| FinMem | `be814aa` | `puppy/prompts.py`, `puppy/reflection.py`, `puppy/agent.py`, `puppy/memorydb.py`, `puppy/portfolio.py`, `puppy/environment.py`, `config/tsla_gpt_config.toml`; arm harness `harness/build_corpus.py`, `harness/render_config.py`, `harness/corpus_config.json` |
| TradingAgents | `a33fd4c` | `tradingagents/agents/analysts/*.py`, `agents/researchers/*.py`, `agents/managers/*.py`, `agents/trader/trader.py`, `agents/risk_mgmt/*.py`, `agents/utils/{agent_utils,agent_states,memory,schemas,structured,rating,*_tools}.py`, `dataflows/{interface,y_finance,yfinance_news,alpha_vantage_fundamentals,stockstats_utils,market_data_validator,stocktwits,reddit}.py`, `graph/{setup,analyst_execution,conditional_logic,propagation,reflection,signal_processing,trading_graph}.py`, `default_config.py` |
| FinAgent | `17248a0` | `res/prompts/module/trading/*.html` (all 31), `res/prompts/template/valid/*/decision.html`, `res/prompts/asset_infos/exp_stocks.json`, `res/prompts/trader/*.txt`, `res/strategy_record/trading/TSLA/*`, `finagent/prompt/{helper,custom}.py`, `finagent/prompt/trading/*.py`, `finagent/tools/strategy_agents.py`, `finagent/environment/trading.py`, `finagent/plots/{interface,kline}.py`, `finagent/data/dataset.py`, `finagent/query/*.py`, `finagent/provider/provider.py`, `configs/exp/*/TSLA*.py`, `tools/main*.py` |

All three clones were verified at the recorded pin before reading (`git rev-parse
HEAD` in each clone's own `.git`; the FinMem clone carries one untracked
directory, `data-pipeline/Fake-Sample-Data/`, which is not a modification of any
tracked source).

## The protocol, restated for material classes

The null-class protocol asked one question per class × engine: does the
perturbation survive into the prompt the decision is made from, or is it
contradicted, erased or diluted downstream. A material class asks the same
question and then two more, because a material class is supposed to *move* the
decision, and a prediction about movement needs the rest of the decision's
input to hold still.

Five dimensions, established and cited per cell:

1. **Expressibility.** Can the manipulation be written into the perturbable text
   at the engine's interception point. The interception points are the
   null audit's (memory rows; a fixture vendor in `VENDOR_METHODS`; substituted
   processed data) and are corrected below where this reading found them
   incomplete.
2. **Survival to the decision.** Does the manipulated content reach the prompt
   the decision is made from, and through how many lossy stages. The
   `lossy_stages_before_decision` counts (0 / 2 / 1) were re-verified for these
   classes rather than carried over.
3. **Contradiction by injected identity or context.** The N2 mechanism, widened
   to figures: does the scaffold inject, independently of the perturbed text,
   anything that still asserts the unperturbed state — a fetched financial
   statement, a price row, a momentum string, a chart.
4. **Competing unperturbed channels.** What evidence reaches the decision that
   the perturbation does not touch, and what share of the decision's input the
   perturbed channel represents. Where unperturbed channels can rationally
   dominate, that is a finding about the sensitivity threshold and is recorded
   even where the verdict is RUN.
5. **Predicted-direction well-formedness.** Whether a single direction of
   decision change can be predicted in advance, or whether the engine's output
   granularity (discrete action, neutral band, feasibility rules) makes a
   correct non-change possible.

Five verdicts. The first three keep their null-audit meanings; the last two are
material-specific:

- **RUN** — the perturbation reaches the decision prompt intact and the predicted
  direction is well defined.
- **RUN, ATTENUATED** — it reaches the decision through a lossy stage. Valid;
  effect size not comparable across engines without saying so. **Not a drop.**
- **DROPPED** — contradicted or erased downstream. Measuring it would measure the
  contradiction.
- **NO TARGET** — the construct the class perturbs does not exist in this engine,
  so there is nothing to manipulate. Distinct from DROPPED: nothing is
  contradicted, because nothing is there.
- **UNDETERMINED** — the source read does not settle it. Must name the specific
  file, artifact or upstream question that would.

A verdict without a `file:line` citation is not a verdict. Prompt templates,
static asset files and config defaults count as source and were read.

## The matrix

| class | FinMem `be814aa` | TradingAgents `a33fd4c` | FinAgent `17248a0` |
|---|---|---|---|
| **M1** surprise-sign flip | **RUN** | **DROPPED** — income statement fetched by ticker | **RUN, ATTENUATED** (severe; precondition: no future price rows) |
| **M2** internals flip | **RUN** | **DROPPED** — same channel, stronger | **RUN, ATTENUATED** (severe; direction weakly formed) |
| **M3** sentiment-lexicon inversion | **RUN** — scoped: not the instrument's own 3-day price direction | **RUN, ATTENUATED** — scoped: not price, not reported figures | **RUN, ATTENUATED** — scoped: not price |
| **M4** failure-condition activation | **NO TARGET** | **NO TARGET** | **NO TARGET** — strategy docs exist only in a config with no news channel |
| **M5** magnitude scaling | **RUN** | **RUN, ATTENUATED** — scoped: not price, not reported figures | **RUN, ATTENUATED** — scoped: not price |

No cell is UNDETERMINED. Two engine-level preconditions on FinAgent (the
substituted price frame must end at the decision date; the decision template and
entry point must be registered) are lead decisions that the registered
interception point can enforce mechanically, and are recorded as preconditions
rather than as open verdicts — see the FinAgent section.

Where a verdict differs from what the class definition would naively predict, the
engine section says why.

### Interception points — reused, and corrected

| engine | null-audit interception | correction from this reading |
|---|---|---|
| FinMem | memory rows via `harness/build_corpus.py` | none needed; but the builder's number-preservation gate rejects every material variant (below) |
| TradingAgents | fixture vendor in `VENDOR_METHODS` | **insufficient at this pin**: the sentiment analyst's StockTwits and Reddit fetches, the verified market snapshot, the identity lookup and the memory log all bypass the registry (below) |
| FinAgent | substitute the processed data | sufficient, with one obligation it did not previously carry: the substituted price frame must not extend past the decision date, or the K-line image shows the future (below) |

---

## FinMem — `be814aa`

**Lossy stages: 0, re-verified.** The decision prompt is `test_prompt`
(`puppy/prompts.py:41-53`) around an `investment_info` string assembled at
`puppy/reflection.py:319-349`: ticker-and-date prefix (`prompts.py:16`), the
retrieved short-term rows joined verbatim with only `.strip()`
(`reflection.py:322-328`), a static paragraph about sentiment scores
(`prompts.py:17-24`, appended at `reflection.py:327`), the mid / long /
reflection layers or their placeholders (`reflection.py:162-188`, `329-346`), and
a momentum block that is emitted only when `momentum` is truthy
(`reflection.py:347-349`). Truncation exists only for `tgi` backbones
(`puppy/agent.py:33-34`, `193`), so nothing in the text is shortened for a GPT
backbone. The guardrails reask (`reflection.py:424-426`) re-sends the same input.

**What else reaches the decision, and what it represents.** The fixture is one
short-memory row (`harness/build_corpus.py:58`, `DECISION_NEWS_ITEMS = 1`) among
the four neutral training rows the corpus writes so the agent does not crash on
empty news (`harness/corpus_config.json` `training_news`). Retrieval takes
`top_k = 3` of those five (`config/tsla_gpt_config.toml:8`; `agent.py:188-192`),
ranked by similarity to the persona string — the query text is
`character_string`, not the news (`agent.py:189`, `212`, `236`, `259`) — merged
with a randomly initialized importance score (`puppy/memorydb.py:96-98`,
`memory_functions/importance_score.py:31-35`; ranking at `memorydb.py:138-218`).
Price enters the prompt as a **sign only**: `Portfolio.get_moment` reduces the
3-day cumulative return to −1 / 0 / +1 (`puppy/portfolio.py:88-110`) and
`_add_momentum_info` renders it as one English sentence
(`reflection.py:227-243`); the raw price never appears. Filings would enter the
mid and long layers (`agent.py:167-177`) but the harness omits them
(`build_corpus.py:97-98`). The persona itself is **not** in the decision prompt —
it is passed nowhere in `trading_reflection` (`agent.py:404-419`). So by
construction the fixture row is the only decision-relevant variable content; the
news channel's share of the decision input is effectively the whole of it. One
caveat the null audit already recorded applies with more force here: because
ranking is by persona similarity plus a random importance draw, a given rep can
retrieve three training rows and **omit the fixture** from the prompt entirely. The
agent logs its retrieved rows (`agent.py:208-209`, "Top-k Short"); the harness
should read that log and flag any rep whose prompt did not contain the fixture,
since such a rep measures nothing about the item.

**M1 surprise-sign flip — RUN.** Expressible: the decision corpus takes an
arbitrary string (`build_corpus.py:195-200`; `day_record` at `72-100`). Survives
verbatim (`reflection.py:325`). Nothing in the engine asserts the reported or the
expected figure independently: no fundamentals fetch, no filings in the harness,
price as a sign. The nearest thing to an independent assertion is a persona line
recalling "certain quarters where revenue missed Wall Street expectations"
(`config/tsla_gpt_config.toml:22`), which is historical, undated, and — as
above — not in the prompt. Direction: a beat that becomes a miss predicts a shift
toward `sell` on a three-way output whose instruction discourages `hold`
(`prompts.py:46-47`; choices validated at `reflection.py:108-112`). A `hold`
→ `hold` non-change is admissible and is not evidence against sensitivity; the
prediction is an ordinal shift, not a specific action.

**M2 internals flip — RUN.** Same path. The definition's requirement that the
decision path "see more than the headline" is met trivially: the news is one
string read by one LLM call; there is no headline / body distinction and no
summarizer to lose the internals in. Direction is predicted (toward less bullish)
but weakly formed: a mixed item is exactly where a rational decision is `hold`
before and after, so a null here is compatible with a correct reading of both
texts. Record the cell as run; read a non-change at face value.

**M3 sentiment-lexicon inversion — RUN, scoped.** Same path; no fundamentals to
contradict. The one independent assertion of direction is the momentum sentence,
and it asserts the sign of the instrument's own 3-day price path
(`reflection.py:227-243`, from `portfolio.py:92-110`). If the fixture's inverted
language is about that path ("shares surged" ↔ "shares plunged"), then in the
negative-momentum context the base or the variant contradicts the momentum line
and the other agrees with it — the N2 shape, sign-flavoured. In the flat context
(`moment == 0`) the block is omitted altogether (`reflection.py:347`, falsy zero;
`corpus_config.json` `_prices` note) and no contradiction is possible. Fixture rule,
recorded as registration content: **M3 directional language must describe
events, results or guidance, never the instrument's own recent price
direction**; under that rule the class runs in every frozen context. Direction:
well formed (the inversion predicts the opposite side).

**M4 failure-condition activation — NO TARGET.** The class requires the engine to
expose documented strategy logic with invalidation conditions and to veto by
citing the named field. FinMem exposes none: the test prompt carries no strategy
rules (`prompts.py:41-53`); its only condition-keyed instruction is a
risk-appetite sentence keyed to the momentum sign ("When cumulative return is
positive or zero, you are a risk-seeking investor", `prompts.py:44`), which is
computed from prices, not read from news, and is not an invalidation condition
of anything. The persona (`tsla_gpt_config.toml:12-23`) lists sectors and one
historical sentence and is not in the prompt. The output schema has no veto and
no field to cite — `investment_decision`, `summary_reason`, memory indices
(`reflection.py:107-136`). The nearest construct is the reflection layer, which
stores the agent's own past `summary_reason` text (`agent.py:421-426`); it is
agent-authored prose about past days, not logic with conditions, and there is
nothing in it for a fixture to activate by name. Nothing to inject; nothing to
contradict.

**M5 magnitude scaling — RUN.** Same path. The momentum line carries sign and no
magnitude (`portfolio.py:94-110`), so a rescale that preserves sign is never
contradicted by it even when the rescaled figure is a price move — the
scoping that M3 needs, M5 does not. Direction: monotone (a larger adverse move
predicts a shift further toward `sell`), on a three-way output where both
magnitudes can legitimately map to the same action; the qualitative threshold the
class straddles is the fixture designer's claim and must be stated per item.

**Harness prerequisite, not an engine finding.** The corpus builder's §4.2 gate,
`check_numbers_preserved` (`harness/build_corpus.py:254-273`), refuses any variant
that drops a number present in the base text. That is correct for the null
classes and rejects **every** M1, M2 and M5 variant, and every M3 variant whose
figures were adjusted to match. The gate must become class-aware — subset check
for null classes, a declared figure-substitution map for material classes —
before a material corpus can be built. Enforcement of drops is unchanged:
`excluded_klasses` with a mandatory reason (`build_corpus.py:343-359`).

---

## TradingAgents — `a33fd4c`

**The architecture at this pin, re-read.** Two things the null audit stated need
correcting before any material verdict can be read against them.

1. **Four analyst reports, not five.** The default selection is `("market",
   "social", "news", "fundamentals")` (`graph/setup.py:62`), and at this pin the
   `social` key builds the **sentiment** analyst
   (`graph/analyst_execution.py:28-38`; `agents/analysts/social_media_analyst.py:1-9`
   is a deprecation shim). There is no separate social report.
2. **The fixture news reaches two of the four.** The news analyst fetches it by
   tool call (`analysts/news_analyst.py:20-28` → `agents/utils/news_data_tools.py:24`
   → `dataflows/interface.py:168-202`). The sentiment analyst **pre-fetches the
   same tool's function directly** into its prompt, for a fixed seven-day window
   (`analysts/sentiment_analyst.py:70`, window at `47-48` and `64`; injected at
   `136-146`). Both go through `route_to_vendor`, so a fixture vendor serves
   both. The channel-share descriptor is therefore **2 of 4**, not 1 of 5, with
   the qualification that the sentiment analyst mixes the news with two live
   social feeds (below).

**Lossy stages: 2 at the registered grain, re-verified; ≥ 3 at fine grain.** The
registered count groups "the report" and "the debate". Read finely: the
news-analyst report and the sentiment report are handed verbatim to the bull and
bear researchers (`researchers/bull_researcher.py:37-43`,
`bear_researcher.py:39-45`; one round, `default_config.py:110`) and to all three
risk debators (`risk_mgmt/aggressive_debator.py:30-35`, `conservative_debator.py:30-35`,
`neutral_debator.py:30-35`; one round, `default_config.py:111`). The research
manager sees only the debate history (`managers/research_manager.py:43-44`); the
trader sees only the research plan (`trader/trader.py:43-48`); the portfolio
manager, who makes the decision, sees the plan, the trader's proposal, the risk
debate history and the memory-log context (`managers/portfolio_manager.py:56-61`)
— **never a report**. The shortest path from fixture text to the decision-maker
is report → risk-debator argument → portfolio manager: three LLM rewrites. The
count of 2 is kept as the registered coarse descriptor and this is recorded
beside it.

**What else reaches the decision.** The market report (OHLCV via
`agents/utils/core_stock_tools.py:24` → `dataflows/y_finance.py:18-70`; indicators;
and a deterministic verified snapshot, `market_data_validation_tools.py:5`, `23`);
the fundamentals report (below); the sentiment report's two social blocks; the
memory-log `past_context` of prior decisions and reflections
(`graph/trading_graph.py:423`; `agents/utils/memory.py:70-95`; injected at
`portfolio_manager.py:36-41`); and the resolved identity string in every prompt
(the N2 mechanism, `agents/utils/agent_utils.py:122-169`). Final signal: a
five-tier rating parsed from the portfolio manager's structured output
(`agents/schemas.py:44-51`, `188-202`; `agents/utils/rating.py:28-48`, default
`Hold` at `48`).

**Interception point — incomplete at this pin.** Five inputs bypass
`VENDOR_METHODS` and must be frozen or stubbed by other means before any class,
null or material, is run:

- StockTwits and Reddit, fetched over HTTP directly by the sentiment analyst
  (`sentiment_analyst.py:43-44`, `71-72`; `dataflows/stocktwits.py:41`, `26`;
  `dataflows/reddit.py:191`, `37-38`). They degrade to an `<... unavailable>`
  placeholder on failure (`stocktwits.py:58`), which is the deterministic state
  a harness should hold them in.
- The verified market snapshot, built from a five-year cached download
  (`market_data_validation_tools.py:5`; `dataflows/market_data_validator.py:35`;
  `dataflows/stockstats_utils.py:148-175`).
- Instrument identity, a live `yf.Ticker(...).info` lookup
  (`agent_utils.py:78-99`).
- The memory log at `~/.tradingagents/memory/trading_memory.md`
  (`default_config.py:75`), read at run start; if it holds *pending* entries the
  run first fetches returns and makes a reflection LLM call
  (`trading_graph.py:296-334`, `251-295`).

**M1 surprise-sign flip — DROPPED.** Expressible and surviving: the text reaches
two analysts and is rewritten into a report and a sentiment band. It is
contradicted by an independently fetched figure. The fundamentals analyst is
default-selected and instructed to call `get_fundamentals`, `get_balance_sheet`,
`get_cashflow` and `get_income_statement` (`analysts/fundamentals_analyst.py:18-28`).
With the default vendor (`default_config.py:136`), `get_fundamentals` returns
live `EPS (TTM)`, `Forward EPS` and `Revenue (TTM)` unfiltered by date
(`dataflows/y_finance.py:296-297`, `304`; `curr_date` "not used", `276`), and
`get_income_statement` returns the quarterly income statement as CSV
(`y_finance.py:421-426`, `432`) filtered to fiscal-period-end ≤ the trade date
(`dataflows/stockstats_utils.py:224-235`). A fiscal period ends before its results
are released, so for any earnings-release fixture the reported quarter's actual
revenue and net income are in that CSV on the fixture date. The Alpha Vantage
path is the same in kind (`dataflows/alpha_vantage_fundamentals.py:30-63`). That
report is handed verbatim to the bull, the bear and all three risk debators
(`bull_researcher.py:41`; `aggressive_debator.py:34`). Held at the base state — as
the registered design holds every unperturbed channel — it asserts the actual
the M1 variant moved. That is N2's mechanism with a number in place of a name,
and measuring it would measure the contradiction. Two things would change the
verdict and neither is M1: fixturing the fundamentals vendor with
variant-consistent statements turns the class into a joint text-and-data
perturbation, which needs its own definition; deselecting the fundamentals
analyst (`setup.py:62`) is a different engine configuration than the published
default. Whether the LLM calls the statement tool in a given run is not settled
by source, but a run in which it does not is a run with a degraded fundamentals
report, not a clean M1 cell.

**M2 internals flip — DROPPED, more decisively.** The income statement CSV is
exactly the multi-component detail M2 perturbs — revenue and the components
below it, by quarter — fetched by ticker, independent of the news, and read by
five of the debate participants. The definition asks for "a decision path that
sees more than the headline"; this engine's fundamentals path sees the whole
statement without the news, which is precisely why the flipped component is
contradicted rather than weighed.

**M3 sentiment-lexicon inversion — RUN, ATTENUATED, scoped.** Survives through
two analysts; the sentiment analyst's structured output — a six-band direction
and a 0–10 score (`schemas.py:258-303`) — is a stage built to register exactly
the kind of change a lexicon inversion makes, so survival into the band is the
expected case, and then into the debate at the fine-grained depth above.
Contradiction is sub-case dependent and the scope is the finding: (a) language
about the instrument's **price path** is contradicted by the market report, which
carries the actual OHLCV and a verified snapshot (`y_finance.py:54-70`;
`market_data_validator.py:1-8`) — dropped for that sub-case; (b) language about
**reported figures** ("revenue surged" ↔ "revenue plunged") inherits M1's drop;
(c) language about **guidance, events, management commentary** has no
independent source — the statements carry no guidance, and `Forward EPS`
(`y_finance.py:297`) is a live consensus figure, a correlate rather than an
assertion. M3 on this engine is runnable on (c) only. Direction: predicted toward
the inverted side on an ordinal five-tier scale; a `Hold` → `Hold` non-change is
admissible.

**M4 failure-condition activation — NO TARGET.** No prompt in the graph documents
strategy logic with invalidation conditions. The market analyst's system message
lists indicator usage tips (`analysts/market_analyst.py:25-53`) — price-indicator
guidance, not conditions a news item could activate. Researchers, debators and
managers carry role instructions only. The structured schemas carry per-run
`entry_price`, `stop_loss`, `price_target` (`schemas.py:139-147`, `216-219`),
which are generated, not documented; the rating enum (`schemas.py:44-51`) has no
veto and nothing to cite. The nearest construct is the memory log: prior
decisions and one-lesson reflections (`graph/reflection.py:20-29`) injected into
the portfolio manager's prompt with an instruction to incorporate them
(`portfolio_manager.py:36-41`; `schemas.py:211-213`). A harness could seed a
resolved entry whose lesson names a condition and then inject that condition in
the news. That is a harness-authored rule, not the agent's own documentation,
and the class as defined does not permit it; if the lead wants it, it is a derived
class with its own definition and its own interception point (the log file), not
M4.

**M5 magnitude scaling — RUN, ATTENUATED, scoped like M3.** A rescaled price move
is contradicted by the market report (dropped sub-case); a rescaled reported
figure inherits M1's drop; a rescaled magnitude the engine has no source for —
a guidance change, a contract value, a unit or delivery figure absent from the
statements — runs. Direction: monotone on the ordinal scale; non-change
admissible.

**Direction and the action alphabet.** The engine's terminal output is five-tier.
The registered materiality scale (TVD over the action distribution,
`docs/readout-rule.md` §2) was worked on a three-action alphabet. Before any
TradingAgents cell is scored, the arm must register either a 5 → 3 mapping or a
five-category TVD, and say which; effect sizes are otherwise not comparable with
the other two engines on top of the attenuation confound already registered.
The parser's default on a malformed decision is `Hold` (`rating.py:28`, `48`),
a hold-biased failure mode of the same kind as FinMem's `reflection.py:447`.

---

## FinAgent — `17248a0`

**Which configuration is "the engine" is not fixed, and it matters more here
than elsewhere.** Six experiment configs pair a decision template with an entry
point. The base config (`configs/exp/trading/TSLA.py:36-40`) uses
`res/prompts/template/valid/trading/decision.html` and is run by
`tools/main.py`. The paper's tool-augmented config
(`configs/exp/trading_mi_w_low_w_high_w_tool_w_decision/TSLA.py:40`) points, at
this pin, at the **non-tool** template `trading_mi-w-low-w-high-w-decision/decision.html`;
the template that actually carries the guidance and strategy blocks
(`template/valid/trading_mi-w-low-w-high-w-tool-w-decision/decision.html:50-52`)
is referenced by no published config, and the only published config that loads a
strategy block is `trading_only_strategy_with_record/TSLA_only_strategy.py:40`,
whose template has **no market-intelligence channel at all**
(`template/valid/only_strategy_trading/decision_with_record.html:11-25`). The
material verdicts below are stated for the news-bearing configurations; the
template choice changes the competing channels and the decision rules but not,
as it turns out, any verdict except where said.

**Lossy stages: 1 on the direct path, re-verified; 2 on the indirect ones.** The
fixture rows enter as `title` and `text` (`finagent/data/dataset.py:106`;
`finagent/prompt/trading/latest_market_intelligence_summary.py:72-80`), beside
the day's OHLC and adjusted close (`57-63`), into the latest-summary prompt,
whose output is ≤ 40 tokens per item and a ≤ 300-token summary carrying an
explicit POSITIVE / NEGATIVE / NEUTRAL label
(`res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:8-9`,
`19`, `21`). The decision reads that summary directly
(`template/valid/trading/decision.html:21`) — one stage — and also reads the
low-level and high-level reflections, each of which consumed the same summary
(`template/valid/trading/low_level_reflection.html:16-21`;
`high_level_reflection.html:14-21`) — two stages. Past market intelligence is
retrieved by the summarizer's own generated query (`finagent/prompt/helper.py:248-321`),
so which past rows appear can change with the perturbation; that is the agent's
behaviour, as with FinMem's retrieval.

**What else reaches the decision.** In every news-bearing template: the company
profile (N2, `decision_task_description_trading.html:2`); the trader persona
(`res/prompts/trader/*.txt`); today's OHLC in the summarizer prompt; the
low-level reflection, itself made from a K-line image with MA and Bollinger
overlays (`low_level_reflection_kline_chart_trading.html:2-15`;
`finagent/plots/interface.py:31-64`) plus **numeric** 1 / 7 / 14-day past returns
as percentages (`finagent/prompt/trading/low_level_reflection.py:60-68`;
`low_level_reflection_price_change_description_trading.html:3-5`); the
high-level reflection from a trading-chart image and the last 14 actions
(`high_level_reflection_trading_chart_trading.html:2-13`); the state line —
adjusted close, position, cash, profit, yesterday's return
(`decision_state_description_trading.html:2`; `finagent/prompt/trading/decision.py:42-52`);
and memory rows that carry past news together with their OHLC
(`latest_market_intelligence_summary.py:167-176`). No fundamentals: the dataset
holds prices, news, guidance, sentiment, economics (`dataset.py:53`;
`finagent/environment/trading.py:31-35`), and no income statement is fetched
anywhere. The image channel is confirmed at source as before
(`finagent/provider/provider.py:270-284`, `411-444`; `finagent/prompt/custom.py:81-96`).

**Precondition — the K-line image can show the future, and the interception
point must prevent it.** The state's price frame runs from `look_back_days`
before to `look_forward_days` *after* the decision date
(`environment/trading.py:121-125`; 14 days, `configs/exp/trading/TSLA.py:25-26`).
`plot_kline` truncates that frame at today **only when told it is not in train
mode** (`finagent/plots/kline.py:32-33`), and `tools/main.py:232` calls it
without `mode`, taking the default `"train"` (`plots/interface.py:31`, forwarded
at `59`). Under the base config's entry point, the valid-mode K-line image
therefore carries up to fourteen days of post-decision prices — the market's
actual reaction to the true event — into the low-level reflection and from there
into the decision. The three `main_mi_w_*` entry points pass `mode` and truncate
(`tools/main_mi_w_low_w_high_w_tool_w_decision.py:231`; the other two at `:232`).
Under `tools/main.py` with the upstream dataset layout, **no perturbation class,
null or material, measures news sensitivity**, because the decision is made with
the answer in view. The registered interception point closes this without
touching the engine: the substituted price frame simply ends at the decision date,
and `days_future` clamps to the last row (`trading.py:122`). That is now an
obligation of the FinAgent harness, verified by its corpus check, and every
FinAgent verdict below is stated under it. (A wrapper that steps the environment
after deciding needs one further row, `trading.py:266`; a wrapper that calls
`run_step` alone, `tools/main.py:226`, does not.)

**M1 surprise-sign flip — RUN, ATTENUATED (severe), under the precondition.**
Expressible: free strings. Survives as the summarizer chooses to carry it — the
label is instructed to prefer a clear POSITIVE or NEGATIVE over NEUTRAL
(`market_intelligence_latest_summary_prompt_trading.html:8`), so a beat that
becomes a miss is the kind of change the label is built to register; the figures
themselves may not survive forty tokens. No independent assertion of the reported
or expected figure exists on this engine. Today's OHLC beside the news
(`latest_market_intelligence_summary.py:57-63`) and the chart up to today are
**correlates** of the true event — a miss variant sitting beside a rally row is
implausible but not contradicted — and are recorded as competing channels, not
as a drop. Direction: toward `SELL` on a three-way output whose rules push away
from `HOLD` (`decision_prompt_trading.html:8-9`); non-change admissible.

**M2 internals flip — RUN, ATTENUATED (severe), direction weakly formed.** The
summarizer sees title and text in full; the decision sees ≤ 40 tokens per item.
The internals survive only if the summarizer keeps them, and a mixed item is the
case the label is most likely to call NEUTRAL — at which point decision rule 1
tells the agent to pay the summary *less* attention (`decision_prompt_trading.html:5`)
and the price channels decide. So the predicted direction of an M2 flip on this
engine is "toward whatever the unperturbed price context says", which is not a
prediction about the news. Run, and read a null literally.

**M3 sentiment-lexicon inversion — RUN, ATTENUATED, scoped.** Directional language
about the instrument's own price is contradicted three ways: the OHLC row in the
summarizer prompt, the K-line image, and the numeric past-return percentages in
the price-change description (`low_level_reflection.py:63-68`). That sub-case is
dropped. Language about events, results and guidance has no independent source
on this engine (no fundamentals), so the reported-figure sub-case that M1 drops
on TradingAgents runs here — attenuated by the same summarizer. Direction: toward
the inverted side; non-change admissible.

**M4 failure-condition activation — NO TARGET.** The engine does document
strategy logic with invalidation conditions — four strategies, each with the
market regime in which it is "less suitable" or "less effective"
(`decision_strategy_trading.html:3`, `5`, `7`, `9`; `_with_record` variant
`:6-17`; docstrings at `finagent/tools/strategy_agents.py:86`, `118`, `158`,
`206`) — but in no published configuration does that documentation share a prompt
with the news. The only config that loads it has no market-intelligence channel
(`only_strategy_trading/decision_with_record.html`), so a news fixture cannot
reach the decision it would need to activate; every news-bearing config omits the
strategy block. NO TARGET in the strict sense: for the perturbable text there is
nothing to activate. Two further facts, for the record, because a `--cfg-options`
override (`tools/main.py:32-41`) could select the unreferenced tool template
without editing source and put both in one prompt: every invalidation condition
named is a **price-regime** property — range-bound, choppy, trending, volatile —
that the engine observes for itself from the K-line, the past-return percentages
and the strategy signals it computes from the price series
(`helper.py:155-188`); a news sentence asserting the regime is either redundant
with that evidence or contradicted by it. Under that override the cell is DROPPED,
not run. And the output has no veto and no field to cite
(`decision_output_format_trading.html:5`). M4 is not testable on this engine via
the news channel under any configuration.

**M5 magnitude scaling — RUN, ATTENUATED, scoped.** A rescaled price move is
hard-contradicted by the numeric past-return percentages
(`low_level_reflection.py:63-68`) — dropped sub-case. A rescaled event or
reported-figure magnitude has no independent source and runs, attenuated.
Direction: monotone; non-change admissible.

**Direction, feasibility and what is scored.** Output is `BUY` / `HOLD` / `SELL`
(`decision_output_format_trading.html:5`; `decision.py:79`). The environment
coerces an infeasible action to `HOLD` — `SELL` with no position, `BUY` with no
cash (`environment/trading.py:199-229`) — and the run loop overwrites the recorded
action with the environment's (`tools/main.py:208-209`) while the LLM's emitted
action is what the decision returned (`tools/main.py:404`, `407`). The
tool-template rules also forbid the infeasible action in the prompt
(`template/valid/trading_mi-w-low-w-high-w-tool-w-decision/decision.html:74`).
So the frozen context's position and cash determine whether a predicted "toward
sell" can be expressed as `SELL` at all; the arm must register whether the
emitted or the executed action is scored, and a frozen context that makes one
side of the prediction infeasible truncates the direction by construction.

---

## Cross-cutting findings

### 1. A material class is testable on an engine only where the manipulated figure has no independent source inside the engine — and the set of independently sourced figures grows with the engine's tool breadth

FinMem sources one thing independently of the text: the sign of a 3-day return.
FinAgent sources prices — levels, numeric percentage moves, and an image. TradingAgents
sources prices, indicators and full financial statements. Read across the
matrix, M1 and M2 run on FinMem, run attenuated on FinAgent, and are dropped on
TradingAgents; the price-move sub-cases of M3 and M5 are contradicted on all
three (FinMem only in a non-flat context, and only for sign). This is the N2
mechanism generalized from identity to figures: an agent that fetches a figure
by ticker anchors that figure outside the text, and a text perturbation of it
measures the anchoring. Consequence for reporting: the reported-financial
classes are reported as **unavailable against statement-fetching agents**, as a
finding about the class of system, in the same sentence-shape as §7 of the
read-out rule reports N2 — never as a per-engine omission. The ordering of
drops is the attenuation ordering, which is not a coincidence: both are the
engine's data-fetching breadth.

### 2. Directional and magnitude perturbations must never be about the instrument's own price

Every engine injects independently computed price context in English or numbers
(FinMem `reflection.py:227-243`; TradingAgents the market report; FinAgent
`low_level_reflection.py:60-68` and the chart). An M3 or M5 fixture whose
perturbed content is the price path is contradicted on all three. Registered as
a **fixture-construction rule**: material variants perturb events, results,
guidance and commentary; the price is the frozen context's to state.

### 3. M4 has no target in a news channel on any of the three

Only FinAgent documents strategy logic with invalidation conditions, only in a
configuration with no news channel, and every condition it names is a price
regime the engine observes for itself. FinMem and TradingAgents document no
strategy logic at all; their nearest constructs (FinMem's reflection layer,
TradingAgents' memory-log lessons) are agent-authored or harness-seedable prose,
not the agent's own documentation. Consequence: M4 as defined is dropped from
the study for all three engines, with the reason stated as a property of the
class of system — strategy logic, where it exists in these agents, is keyed to
price-regime facts the agent computes rather than reads. If the lead wants a
condition-activation test, it is a memory- or strategy-channel perturbation with
its own interception point, its own definition and its own audit.

### 4. Corrections to the null audit's descriptors, carried forward without editing it

The null audit and matrix are attached to a filed registration and are not
edited. This reading found four descriptors that Registration 2 must state
correctly:

- TradingAgents has **four** analyst reports at `a33fd4c`, not five, and the
  fixture news reaches **two** of them. The registered channel-share
  descriptor "1 of 5" becomes "2 of 4, one of which mixes it with two social
  feeds".
- TradingAgents' registered interception point — a fixture vendor in
  `VENDOR_METHODS` — does not cover StockTwits, Reddit, the verified snapshot,
  the identity lookup or the memory log. Each needs its own freeze.
- TradingAgents' fine-grained lossy count is at least three rewrites to the
  decision-maker, who never sees a report.
- FinAgent's K-line image, under the base config's entry point and the
  upstream dataset layout, includes fourteen post-decision days. This affects
  N1 and N3 on FinAgent exactly as it affects the material classes, and it is
  closed by the harness's substituted price frame ending at the decision date.

### 5. The read-out rule's direction diagnostic inverts for material classes

§10 of the read-out rule reads a consistent direction of shift across items as a
**fixture-quality alarm**, because null-class perturbations are directionless by
construction. For a material class a consistent direction is the **prediction**.
The diagnostic cannot be applied unchanged to material cells; the registration
must state, per class, the predicted sign, and the alarm becomes "movement
against the predicted sign, consistently". A material class whose predicted sign
is not well formed on an engine (M2 on FinAgent, above) has no alarm and no
confirmation — only a magnitude.

### 6. Output granularity differs, and the prediction is ordinal

FinMem and FinAgent decide on three actions; TradingAgents on five tiers; FinAgent
coerces infeasible actions. Every material prediction in this audit is a
direction of shift on an ordinal scale, with a correct non-change admissible on
every engine. Before a material cell is scored, each arm must register its action
alphabet and any mapping to the three-action TVD, and the FinMem and FinAgent
frozen contexts must be checked for feasibility of both sides of every predicted
shift.

### 7. Harness prerequisites this audit creates

Not engine findings; listed so they are not lost between the audit and the
fixture freeze.

- FinMem: `check_numbers_preserved` must become class-aware
  (`harness/build_corpus.py:254-273`); the run log's "Top-k Short" lines must be
  read to flag reps whose prompt omitted the fixture (`agent.py:208-209`).
- TradingAgents: freeze the five bypassing inputs; register the action alphabet.
- FinAgent: the substituted price frame ends at the decision date; register the
  decision template and entry point; register emitted-versus-executed action.
