# Candidate-engine scan, extended — the mechanical sub-question only

**Scanned 2026-09-15.** Scouting-grade, like `docs/candidate-scan.md`, and
subject to the same rule: nothing here is citable in the paper until the engine
is pinned and re-read against a fixed SHA. Unlike the 2026-08-09 scan, every
file below *was* read at a recorded commit, by raw-file fetch, so the line
numbers are exact for that commit; the engines remain un-pinned as study arms.

The material audit (`docs/applicability-audit-material.md`) generalised the
null audit's N2 finding to one sentence: **scaffolds independently re-derive
the content the perturbation alters, so the class measures the contradiction
rather than the sensitivity.** Three payloads were observed across the three
subject engines — instrument identity, reported figures, price path. This scan
asks one mechanical question of four more engines, and nothing else:

> Does the engine fetch or compute, independently of the news text, the figures
> a material perturbation (M1 surprise-sign, M2 internals, M5 magnitude) would
> alter, or the price path any of them implies?

A **counterexample** would be an engine in which the news text is the *only*
source of a figure the decision uses, so that altering the figure in the text
alters the decision's input without contradiction. One was sought in every
engine, and the search is stated per engine below.

| engine | commit read | independently re-derives figures? | payload(s) | counterexample found? |
|---|---|---|---|---|
| CryptoTrade | `210da73` | **yes** | price path; on-chain metrics; technical signals | no |
| FinRobot (Market_Analyst / forecaster) | `6d6ccd3` | **yes** | reported fundamentals; price path; identity | no |
| StockAgent | `e2a9c05` | **yes**, by construction | the event's numeric effect (loan rate) | no |
| QuantAgent/Xiong (QuantHarness) | `2e64c7b` | n/a — no news channel | price path only, all of it | n/a |

Result: **7 for 7 on the mechanism** (three subjects plus four candidates),
**0 counterexamples**. The candidates add one sub-type the subjects did not
show, recorded under StockAgent.

---

## CryptoTrade — `Xtra-Computing/CryptoTrade` @ `210da73af5f17992be425e61305524a5c24dae40`

**What the news could carry.** Crypto news has no earnings, so M1/M2 in their
equity form have no target; the analogues are on-chain figures ("daily
transactions rose 30%") and price moves ("ETH fell 8% overnight"), which are
M5-shaped.

**What the engine re-derives, independently of the news.**

- The state carries the next day's open price and a technical block (SMA,
  Bollinger position, MACD) computed from the price CSV, and the day's on-chain
  transaction statistics from a second CSV: `eth_env.py:37-53` (load and
  compute), `eth_env.py:59-145` (`get_close_state`, price at 132, txn stats at
  104-110, news at 112-126, assembled at 129-145).
- The prompt exposes them as text to a separate on-chain analyst — open price,
  every txn-stat column, every technical column — `env_history.py:28-42`. The
  news analyst sees only the news, `env_history.py:44-45`. The trader sees the
  two analysts' paragraphs side by side, `env_history.py:57-59`,
  `eth_trial.py:74-75`.

**Verdict.** Any figure a material variant plants in the news arrives at the
trader beside an on-chain report computed from the unperturbed series. Same
mechanism as the subjects' price-path payload; here it also covers the on-chain
metrics, which are the crypto analogue of reported figures.

**Counterexample sought.** Is there any figure the trader uses that only the
news supplies? No: the news channel's output is a "one concise paragraph"
trend estimate, and the trader's action is a float in [-1, 1] on the three
reports. Nothing numeric survives from the news channel that the on-chain
channel does not also assert.

## FinRobot, Market_Analyst — `AI4Finance-Foundation/FinRobot` @ `6d6ccd32c1b8b1904dc656cf06897438aba3daec`

**What the news could carry.** Equity news; M1/M2/M5 apply directly (beat vs
miss, margin internals, magnitude of a move).

**What the engine re-derives.** The Market_Analyst's toolkit is exactly four
functions, `finrobot/agents/agent_library.py:41-46`:

- `get_company_profile` — identity injection by ticker (`finnhub_utils.py:34-52`),
  the N2 mechanism, already recorded in the 2026-08-09 scan.
- `get_company_news` — the perturbable channel.
- `get_basic_financials` — `finnhub_utils.py:134-157`: fetches Finnhub's
  `company_basic_financials(symbol, "all")`, takes the **latest quarterly
  value of every series** (`149-151`), and returns the whole metric dictionary
  as JSON. The column list (`138`) includes `epsGrowthQuarterlyYoy`,
  `revenueGrowthQuarterlyYoy`, `grossMarginTTM`, `operatingMarginTTM`,
  `netProfitMarginTTM`, `52WeekHigh/Low`, `5DayPriceReturnDaily`. These are
  the figures M1 and M2 alter, fetched by ticker, unfiltered.
- `get_stock_data` — `yfinance_utils.py:23-37`: the price path by ticker and
  date range.

**Verdict.** This is the TradingAgents mechanism (fundamentals analyst fetches
the income statement) in a single-agent shape, and it is *worse* for a material
class: the fetched figures land as a tool return in the same context as the
news, with no summarisation between them, so the contradiction is maximally
legible to the deciding model. The 0-lossy-stage property that makes FinRobot
attractive for N1/N3 makes it the clearest possible drop for M1/M2.

**Counterexample sought.** Could the tool set be configured without
`get_basic_financials` and `get_stock_data`? The toolkit is a literal list in
`agent_library.py:41-46`; a run that removes two of four tools is a modified
agent, which the protocol forbids. Within the published configuration, no.

## StockAgent — `MingyuJ666/Stockagent` @ `e2a9c052b81694067b1dbed4ccf39be9ab7f392c`

**What the news could carry.** There is no news channel in the usual sense.
Two scripted macro events exist. Each is a fixed sentence posted to the forum
under the system author (`main.py:132-137`), and the event's *content* is a
numeric change to the loan-rate table applied on the same lines
(`util.py:272-281`: `EVENT_1_MESSAGE` with `EVENT_1_LOAN_RATE`,
`EVENT_2_MESSAGE = "The government has announced an increase in interest
rates."` with `EVENT_2_LOAN_RATE`).

**What the engine re-derives.** The agents never read the rate from the
sentence: the loan-decision prompt is templated from `util.LOAN_RATE` directly
(`prompt/agent_prompt.py:26-32`, `{loan_rate1..3}`), and the forum message
reaches them only as one of the previous day's posts (`main.py:142`).

**Verdict.** The mechanism, in its purest form: the text and the figure are
delivered by two channels and only the numeric channel is causal. A material
variant that rewrote "increase" to "decrease" would produce a forum post
contradicted by the rate table every agent is shown. This is a **new sub-type**
for the taxonomy: not *re-derivation* (the engine computing the figure) but
*parallel delivery* (the engine's own configuration carrying the figure beside
the text). The consequence for a suite designer is the same.

**Counterexample sought.** Is there a text-only route to a decision? The forum
is agent-authored prose that other agents read, so in principle an agent could
act on a peer's post that asserts a figure. But the assertable figures — prices,
rates, holdings — are all injected numerically into every agent's prompt each
day, so there is no figure an agent knows *only* from prose. No.

## QuantAgent (Xiong 2025) — `Y-Research-SBU/QuantHarness` @ `2e64c7befa75a88d254a426f5f29fa61b0b56732`

**No news channel.** The state schema is closed (`agent_state.py:6-67`): OHLCV
dictionary, time frame, asset name, computed indicators, two base64 chart
images, three reports, decision. Every figure the decision agent sees
(`decision_agent.py:13-18`) is computed by the engine from the OHLCV. There is
nothing for a material class to perturb, so the question does not arise; the
engine is recorded because it is the limiting case — *every* input is
independently derived, which is where the spectrum ends.

---

## What the extension changes

1. **The one-sentence generalisation holds at 7 for 7 with no counterexample.**
   The claim in the paper can be stated as a property observed in every
   released LLM trading agent examined, across five architectural genres
   (memory-augmented single agent, multi-agent debate, multimodal single agent,
   reflective crypto agent, autogen tool-calling forecaster), plus a market
   simulation and a price-only pipeline as the two limiting cases. The
   provenance caveat stands: four of the seven were scouted at a recorded
   commit, not pinned and audited.
2. **A second sub-type is worth naming.** *Re-derivation* (the scaffold fetches
   or computes the figure: TradingAgents, FinRobot, FinAgent's price row,
   CryptoTrade) versus *parallel delivery* (the figure arrives through
   configuration or state beside the text: StockAgent's loan-rate table, and,
   arguably, FinMem's momentum string). Both defeat a material class the same
   way; distinguishing them tells a suite designer *where* to look before
   spending.
3. **The counterexample search is reportable as a method.** For each engine:
   enumerate the figures the decision prompt contains; for each, ask whether
   the news text is its only source. The search terminates in one reading pass
   per engine and its negative result is what licenses the general claim. The
   paper should say that this was done and how, rather than assert the
   generalisation.
4. **Nothing here touches the registered design.** N1/N3 verdicts are unchanged;
   no candidate becomes a subject.
