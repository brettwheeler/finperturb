# FinAgent K-line lookahead — record

**Status: closed, not sent.** The condition was already reported publicly
upstream on 2025-04-14 at `https://github.com/DVampire/FinAgent/issues/2` by a third
party, quoting the same line and naming the leakage; it is unanswered by the
maintainers as of 2026-09-15, and the repository has not been pushed to since
2024-08-31. The author located that report on 2026-09-15, after this project's
audit had reached the same reading independently, and decided not to send a
separate report: the finding is public, and the one question a report could
add — which entry point produced the paper's figures — is not one the record
suggests would be answered. The paper cites the issue as the prior report and
this audit as an independent confirmation.

Upstream: `https://github.com/DVampire/FinAgent`, pin `17248a0`
(arXiv 2402.18485, KDD 2024). Read 2026-09-15, source only, no engine run.

## What the source establishes

1. **The environment's state window spans past the decision date.**
   `finagent/environment/trading.py:121-125` builds the state's price frame
   from `look_back_days` before the current day to `look_forward_days` after
   it; the published trading configs set `look_forward_days = 14`
   (`configs/exp/trading/TSLA.py:25-26`).
2. **The K-line plotter truncates only when told it is not training.**
   `finagent/plots/kline.py:32-33`: the frame is cut at `now_date` only when
   `mode != "train"`, and the default is `mode = "train"`, under which the
   full window, future rows included, is rendered.
3. **Three entry points never pass the mode through.** `tools/main.py:232`,
   `tools/main_mi_w_decision.py:232` and `tools/main_strategy.py:232` call
   `plots.plot_kline(state=state, info=info, save_dir=save_dir)` with no
   `mode`, inside a `run_step` that receives `mode` and uses it for every
   template choice. The three `main_mi_w_low_w_*` entry points pass
   `mode=mode` (their lines 231–232) and are not affected.
4. **The image reaches the backbone.** `finagent/plots/interface.py:31-59`
   writes the chart; `finagent/provider/provider.py:270-284` base64-encodes it
   into an `image_url` content part of the chat request.
5. **The published run instructions name the affected entry points.** The
   upstream README's *Run* section lists `python main.py` and
   `python main_mi_w_decision.py`, both affected; `main.py` defaults to the
   full-system config `configs/exp/trading/AAPL.py`.

Consequence: in the validation phase of those entry points, every decision
step's chart shows up to fourteen sessions after the decision date, with
moving-average and Bollinger overlays computed across them.

## What the source does not establish

Whether the figures reported in the paper were produced with these entry
points or with the three that pass `mode`. The README's instructions point at
the affected ones, and the six config families map one-to-one onto the six
entry points, but which runs produced which reported number is not recoverable
from the repository. The registration text and the paper therefore say that
the published experiments' exposure is not established by source reading, and
claim no more. The upstream issue does not settle it either: it reports the
code path, not which runs produced the paper's tables.

## What this project does about it

The FinAgent arm's registered interception point substitutes the processed
price frame; the design condition (Registration 1, § Design plan) is that the
substituted frame ends at the decision date, so `days_future` clamps to the
last row and the chart carries no post-decision session whatever the entry
point. No upstream code is modified.

## Log

| date | event |
|---|---|
| 2026-09-15 | Source reading completed; draft report written |
| 2026-09-15 | Prior public report located by the author (issue #2, 2025-04-14, unanswered); decision not to send; draft withdrawn; credit added to the material audit, its matrix, and the registration text |
