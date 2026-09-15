# FinPerturb pilot — FinMem

Logs:

- `arms\finmem\data\runs\rehearsal_neg_momentum.jsonl`

Rows: 40 (40 ok, 0 not ok)

**40 rows carry no context stamp** (written before the field existed).
Their frozen context cannot be verified from the data; that they belong here
rests on how they were run, not on what was recorded.


## Scoring rules in force

| rule | value |
|---|---|
| scoring code | finperturb `f5a57f3` |
| tied baseline | excluded from flip-rate scoring, retained for JSD |
| governing statistic | JSD + permutation null, at every phi |
| materiality scale | net TVD per cell: variant vs base, minus the BASE-vs-FLOOR control |
| flip rate quotable when | phi < 0.2 and baseline not tied |
| permutation resamples | 10,000 (smallest reportable p = 0.0001) |
| root seed | 20260808 (streams derived by name) |
| bootstrap draws | 10,000 |
| multiplicity | Benjamini-Hochberg and Holm, one family over item x class |

Model version: `gpt-5.4-mini-2026-03-17` (single version across all scored rows)


## Decoding floor (phi)

phi = **0.5100** (mean over 2 items)


| item | n | floor actions | phi | 95% CI (resampling this item's runs) |
|---|---|---|---|---|
| S01 | 10 | {'sell': 6, 'hold': 3, 'buy': 1} | 0.5400 | [0.1800, 0.6600] |
| S02 | 10 | {'sell': 4, 'hold': 6} | 0.4800 | [0.1800, 0.5000] |

An item whose phi is high cannot support a flip statistic: its modal baseline is
a coin flip, so a flip rate measured against it reflects which baseline was drawn
rather than what the perturbation did. This is no longer left to the reader to
screen — a flip rate is gated on phi < 0.2 and printed as
a reason rather than a number when it fails. Nothing here gates the JSD tables,
which need no stable mode and are reported for every item.


## PRIMARY — distributional shift (Jensen–Shannon, bits)

Variant action distribution vs the base item's, net of the same-input control.
The control is BASE vs FLOOR: identical text, so its divergence is sampling noise
and nothing else. 0 bits = identical distributions, 1 bit = disjoint.

| klass | items | raw JSD | control JSD | net | 95% CI (bootstrap over items) |
|---|---|---|---|---|---|
| N1 | 1 | 0.2755 | 0.0913 | +0.1842 | [+0.1842, +0.1842] |
| N2 | 0 | — | — | — | not run |
| N3 | 1 | 0.0390 | 0.0913 | -0.0523 | [-0.0523, -0.0523] |

### Per-item JSD, with permutation p-values

p is the share of 10,000 same-input resamples reaching the observed
divergence — i.e. how often the unperturbed text alone produces a shift this large at
these sample sizes. The spread across items is the statistic §7.5 asks for; the mean
hides the one item that moved.

Each cell reads `JSD (raw p / BH / Holm)`. The family is all 2 item × class
tests corrected together, not each class on its own. Raw p is kept beside the
adjusted values and is never dropped: BH controls the false discovery rate and suits
the screen's actual question (which items moved), Holm controls the family-wise error
rate and is the one to read if a single cell would be quoted on its own.

| item | control (BASE vs FLOOR) | N1 (raw / BH / Holm) | N2 (raw / BH / Holm) | N3 (raw / BH / Holm) |
|---|---|---|---|---|
| S01 | 0.0913 | 0.2755 (0.241 / 0.481 / 0.481) | — | 0.0390 (0.859 / 0.859 / 0.859) |
| S02 | 0.0290 | — | — | — |

## MATERIALITY — total-variation distance

TVD is the read-out rule's materiality scale: the share of runs that would have
to land on a different action to explain the shift, so 0.10 always means a tenth
of runs decided differently — on a unanimous baseline and a 70/30 one alike,
which is the linearity JSD does not have. It carries no p-value: significance
lives in the JSD tables above, materiality lives here, and the read-out rule
requires BOTH before a cell is declared moved. This report, as ever, declares
nothing.

| klass | items | raw TVD | control TVD | net | 95% CI (bootstrap over items) |
|---|---|---|---|---|---|
| N1 | 1 | 0.4000 | 0.3000 | +0.1000 | [+0.1000, +0.1000] |
| N2 | 0 | — | — | — | not run |
| N3 | 1 | 0.2000 | 0.3000 | -0.1000 | [-0.1000, -0.1000] |

### Per-item TVD

Each cell reads `raw (net)`, where net subtracts THIS item's own BASE-vs-FLOOR
control — identical text, so the TVD sampling alone produces at these run
counts. The read-out rule's materiality criterion is applied to the net value,
per cell, by the lead — never by this script.

| item | control (BASE vs FLOOR) | N1 raw (net) | N2 raw (net) | N3 raw (net) |
|---|---|---|---|---|
| S01 | 0.3000 | 0.4000 (+0.1000) | — | 0.2000 (-0.1000) |
| S02 | 0.2000 | — | — | — |

## SECONDARY — modal flip rates

Retained because it is the statistic §6–§7 were designed around and it is
legible. It does not govern anything: JSD is primary at every phi, and a flip
rate is quotable only for an item that passes the interpretability gate below.

### Excluded from flip-rate scoring — tied baseline

A tie has no modal action, and picking one by dictionary order would make every
flip rate for that item a measure of the tie-break. These items keep all their
BASE runs and appear in full in every JSD table above.

| item | BASE actions | tied on |
|---|---|---|
| S01 | {'buy': 2, 'sell': 2, 'hold': 1} | buy, sell |

### Per-item flip rate, gated

Quotable when phi < 0.2 and the baseline is not tied;
otherwise the reason is printed in place of the number, because a rate measured
against an unstable baseline reports which baseline was drawn rather than what the
perturbation did.

0 of 2 items pass.

| item | phi | N1 | N2 | N3 |
|---|---|---|---|---|
| S01 | 0.5400 | not interpretable (tied baseline) | — | not interpretable (tied baseline) |
| S02 | 0.4800 | — | — | — |

### Aggregate flip rate

`interpretable` counts how many of the contributing items pass the gate. An
aggregate built mostly from items that fail it inherits their problem — the
number is printed rather than suppressed because it is an input to nothing, but
it is not quotable on a row where that count is short of the item count.

| klass | items | interpretable | runs | raw | phi (these items) | net (raw − phi) | 95% CI (bootstrap over items) |
|---|---|---|---|---|---|---|---|
| N1 | 0 | 0/0 | 0 | — | — | — | not run |
| N2 | 0 | 0/0 | 0 | — | — | — | not run |
| N3 | 0 | 0/0 | 0 | — | — | — | not run |

The bootstrap resamples items and there are 2, so the interval is
degenerate rather than precise. Intervals are uninformative below roughly 10 items.


## Baseline actions

`margin` is the top action's share minus the runner-up's. The tie test is binary
and arbitrariness is not: a 9-vs-8 split passes the test and is worth barely more
than 8-vs-8, and only the margin shows it. Reported, not acted on — no rule was
pre-registered against it.

| item | baseline (modal BASE) | margin | BASE actions |
|---|---|---|---|
| S01 | TIE (buy, sell) | +0.000 | {'buy': 2, 'sell': 2, 'hold': 1} |
| S02 | sell | +0.200 | {'sell': 3, 'hold': 2} |

N1 JSD spread: min 0.2755 / median 0.2755 / max 0.2755

N3 JSD spread: min 0.0390 / median 0.0390 / max 0.0390


## Directional shift (diagnostic, not in §7)

Mean change in each action's share, variant minus base, averaged over items.
Near-zero means the perturbation moved decisions in no consistent direction —
what instability looks like. A large consistent shift points at the VARIANTS
rather than the agent, and should be read as a fixture-quality alarm.

| klass | Δ buy | Δ hold | Δ sell | max abs |
|---|---|---|---|---|
| N1 | -0.400 | +0.400 | +0.000 | 0.400 |
| N3 | -0.200 | +0.000 | +0.200 | 0.200 |


## Marginal action distribution (addition to §7)

| klass | actions |
|---|---|
| FLOOR | {'sell': 10, 'hold': 9, 'buy': 1} |
| BASE | {'buy': 2, 'hold': 3, 'sell': 5} |
| N1 | {'hold': 3, 'sell': 2} |
| N3 | {'sell': 3, 'hold': 1, 'buy': 1} |

A degenerate distribution here makes a low flip rate uninformative: an agent
that answers the same way to everything cannot flip.

