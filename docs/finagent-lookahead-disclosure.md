# FinAgent K-line lookahead — upstream disclosure record

**Status: DRAFT, not sent.** Recipient and sending address to be fixed by the
project lead. This file records what source reading establishes, what it does
not, and the text to send. It is kept in the repository so the paper can say
that the finding was reported upstream, and when.

Upstream: `https://github.com/DVampire/FinAgent`, pin `17248a0`
(arXiv 2402.18485). Read 2026-09-15, source only, no engine run.

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
claim no more.

## What this project does about it

The FinAgent arm's registered interception point substitutes the processed
price frame; the design condition (Registration 1, § Design plan) is that the
substituted frame ends at the decision date, so `days_future` clamps to the
last row and the chart carries no post-decision session whatever the entry
point. No upstream code is modified.

## Draft report to upstream (private, before publication)

> Subject: Possible validation-phase lookahead through the K-line image in
> FinAgent (`17248a0`)
>
> I am auditing FinAgent as one of three engines in a perturbation study
> (pre-registered; repository to be public shortly) and want to raise one
> reading privately before anything is published, in case I have misread the
> code or the published experiments used a path that is not affected.
>
> `finagent/plots/kline.py` truncates the price frame at the current date only
> when `mode != "train"`, and defaults to `"train"`. In `tools/main.py`,
> `tools/main_mi_w_decision.py` and `tools/main_strategy.py`, `run_step`
> receives `mode` but calls `plots.plot_kline(...)` without passing it, so in
> the validation phase the rendered chart spans the environment's full state
> window, which the trading configs set to fourteen days past the decision
> date (`look_forward_days = 14`). The chart is base64-encoded into the request
> in `provider.py`. The three `main_mi_w_low_w_*` entry points pass
> `mode=mode` and are not affected.
>
> Two questions. First, is this reading correct? Second, were the results in
> the paper produced with the entry points that pass `mode`, or with `main.py`
> / `main_mi_w_decision.py` as the README's Run section suggests?
>
> In our own study we close this at our interception point by ending the
> substituted price frame at the decision date, so no claim we make depends
> on the answer; we would simply like the record to be accurate and to give
> you the opportunity to respond first. I will note in the paper that this was
> reported to you and on what date.

## Log

| date | event |
|---|---|
| 2026-09-15 | Source reading completed; draft written; not sent |
