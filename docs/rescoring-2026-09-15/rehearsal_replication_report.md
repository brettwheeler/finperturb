# FinPerturb pilot — FinMem

Logs:

- `arms\finmem\data\runs\rehearsal_replication.jsonl`

Rows: 360 (360 ok, 0 not ok)

**360 rows carry no context stamp** (written before the field existed).
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

phi = **0.4067** (mean over 4 items)


| item | n | floor actions | phi | 95% CI (resampling this item's runs) |
|---|---|---|---|---|
| S04 | 30 | {'buy': 10, 'hold': 20} | 0.4444 | [0.2778, 0.5000] |
| S05 | 30 | {'hold': 25, 'buy': 5} | 0.2778 | [0.0644, 0.4200] |
| S06 | 30 | {'buy': 6, 'hold': 21, 'sell': 3} | 0.4600 | [0.2400, 0.5978] |
| S07 | 30 | {'hold': 10, 'sell': 20} | 0.4444 | [0.2778, 0.4978] |

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
| N1 | 4 | 0.2354 | 0.0566 | +0.1788 | [+0.0134, +0.3441] |
| N2 | 0 | — | — | — | not run |
| N3 | 4 | 0.1720 | 0.0566 | +0.1154 | [-0.0026, +0.2718] |

### Per-item JSD, with permutation p-values

p is the share of 10,000 same-input resamples reaching the observed
divergence — i.e. how often the unperturbed text alone produces a shift this large at
these sample sizes. The spread across items is the statistic §7.5 asks for; the mean
hides the one item that moved.

Each cell reads `JSD (raw p / BH / Holm)`. The family is all 8 item × class
tests corrected together, not each class on its own. Raw p is kept beside the
adjusted values and is never dropped: BH controls the false discovery rate and suits
the screen's actual question (which items moved), Holm controls the family-wise error
rate and is the one to read if a single cell would be quoted on its own.

| item | control (BASE vs FLOOR) | N1 (raw / BH / Holm) | N2 (raw / BH / Holm) | N3 (raw / BH / Holm) |
|---|---|---|---|---|
| S04 | 0.0624 | 0.4064 (0.000 / 0.000 / 0.001) | — | 0.4224 (0.000 / 0.001 / 0.001) |
| S05 | 0.0627 | 0.1245 (0.020 / 0.040 / 0.100) | — | 0.0503 (0.242 / 0.242 / 0.472) |
| S06 | 0.0408 | 0.3852 (0.000 / 0.000 / 0.001) | — | 0.1476 (0.028 / 0.045 / 0.113) |
| S07 | 0.0604 | 0.0255 (0.236 / 0.242 / 0.472) | — | 0.0677 (0.070 / 0.094 / 0.211) |

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
| N1 | 4 | 0.4500 | 0.1875 | +0.2625 | [-0.0125, +0.5333] |
| N2 | 0 | — | — | — | not run |
| N3 | 4 | 0.3750 | 0.1875 | +0.1875 | [-0.0083, +0.4292] |

### Per-item TVD

Each cell reads `raw (net)`, where net subtracts THIS item's own BASE-vs-FLOOR
control — identical text, so the TVD sampling alone produces at these run
counts. The read-out rule's materiality criterion is applied to the net value,
per cell, by the lead — never by this script.

| item | control (BASE vs FLOOR) | N1 raw (net) | N2 raw (net) | N3 raw (net) |
|---|---|---|---|---|
| S04 | 0.1333 | 0.7000 (+0.5667) | — | 0.7000 (+0.5667) |
| S05 | 0.2333 | 0.4000 (+0.1667) | — | 0.2000 (-0.0333) |
| S06 | 0.1500 | 0.6500 (+0.5000) | — | 0.3500 (+0.2000) |
| S07 | 0.2333 | 0.0500 (-0.1833) | — | 0.2500 (+0.0167) |

## SECONDARY — modal flip rates

Retained because it is the statistic §6–§7 were designed around and it is
legible. It does not govern anything: JSD is primary at every phi, and a flip
rate is quotable only for an item that passes the interpretability gate below.

### Per-item flip rate, gated

Quotable when phi < 0.2 and the baseline is not tied;
otherwise the reason is printed in place of the number, because a rate measured
against an unstable baseline reports which baseline was drawn rather than what the
perturbation did.

0 of 4 items pass.

| item | phi | N1 | N2 | N3 |
|---|---|---|---|---|
| S04 | 0.4444 | not interpretable (phi = 0.444) | — | not interpretable (phi = 0.444) |
| S05 | 0.2778 | not interpretable (phi = 0.278) | — | not interpretable (phi = 0.278) |
| S06 | 0.4600 | not interpretable (phi = 0.460) | — | not interpretable (phi = 0.460) |
| S07 | 0.4444 | not interpretable (phi = 0.444) | — | not interpretable (phi = 0.444) |

### Aggregate flip rate

`interpretable` counts how many of the contributing items pass the gate. An
aggregate built mostly from items that fail it inherits their problem — the
number is printed rather than suppressed because it is an input to nothing, but
it is not quotable on a row where that count is short of the item count.

| klass | items | interpretable | runs | raw | phi (these items) | net (raw − phi) | 95% CI (bootstrap over items) |
|---|---|---|---|---|---|---|---|
| N1 | 4 | 0/4 | 80 | 0.6625 | 0.4067 | +0.2558 | [-0.1069, +0.4889] |
| N2 | 0 | 0/0 | 0 | — | — | — | not run |
| N3 | 4 | 0/4 | 80 | 0.5125 | 0.4067 | +0.1058 | [-0.0861, +0.3597] |

At least one class aggregates items whose own flip rate is not interpretable.
Read the per-item table above and the PRIMARY JSD table instead.


## Baseline actions

`margin` is the top action's share minus the runner-up's. The tie test is binary
and arbitrariness is not: a 9-vs-8 split passes the test and is worth barely more
than 8-vs-8, and only the margin shows it. Reported, not acted on — no rule was
pre-registered against it.

| item | baseline (modal BASE) | margin | BASE actions |
|---|---|---|---|
| S04 | hold | +0.500 | {'hold': 14, 'buy': 4, 'sell': 2} |
| S05 | hold | +0.250 | {'hold': 12, 'buy': 7, 'sell': 1} |
| S06 | hold | +0.650 | {'hold': 16, 'sell': 3, 'buy': 1} |
| S07 | sell | +0.800 | {'sell': 18, 'hold': 2} |

N1 JSD spread: min 0.0255 / median 0.2548 / max 0.4064

N3 JSD spread: min 0.0503 / median 0.1076 / max 0.4224


## Directional shift (diagnostic, not in §7)

Mean change in each action's share, variant minus base, averaged over items.
Near-zero means the perturbation moved decisions in no consistent direction —
what instability looks like. A large consistent shift points at the VARIANTS
rather than the agent, and should be read as a fixture-quality alarm.

| klass | Δ buy | Δ hold | Δ sell | max abs |
|---|---|---|---|---|
| N1 | +0.437 | -0.400 | -0.038 | 0.437 |
| N3 | +0.225 | -0.137 | -0.087 | 0.225 |


## Marginal action distribution (addition to §7)

| klass | actions |
|---|---|
| FLOOR | {'buy': 21, 'hold': 76, 'sell': 23} |
| BASE | {'hold': 44, 'sell': 24, 'buy': 12} |
| N1 | {'buy': 47, 'hold': 12, 'sell': 21} |
| N3 | {'buy': 30, 'sell': 17, 'hold': 33} |

A degenerate distribution here makes a low flip rate uninformative: an agent
that answers the same way to everything cannot flip.

