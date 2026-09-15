# N3 distractor incorporation — exploratory, pilot rows only

Generated 2026-09-15 12:06:49Z at `f5a57f3` by `scripts/analyze_n3_incorporation.py`.

**Status: exploratory.** Not a registered analysis; governs nothing. The rows are the fabricated-fixture rehearsal runs disclosed in Registration 1 (§ Existing data). This asks a mechanistic side question: when N3 appends an irrelevant sentence, does the agent's rationale mention it, and does the action differ from the modal BASE action more often when it does.

Rows: 670 across 4 logs; N3 rows with status ok: 125; non-N3 control rows: 545.

## Clauses and detectors

| variant | corpus | item | appended clause | detector terms |
|---|---|---|---|---|
| S01-N3-1 | smoke | S01 | The company's visitor centre completed a lobby refurbishment earlier this spring. | visitor centre, visitor center, lobby, refurbish |
| S03-N3-1 | borderline | S03 | The company's visitor centre will extend its weekend opening hours from next month. | visitor centre, visitor center, weekend, opening hours |
| S04-N3-1 | replication | S04 | The company will publish its annual sustainability report on its investor relations website later this month. | sustainability |
| S05-N3-1 | replication | S05 | The company's Fremont site completed a scheduled repaving of its staff car park over the summer. | car park, parking, repav, fremont |
| S06-N3-1 | replication | S06 | The company added two new languages to its owner's manual portal earlier this year. | owner's manual, owner’s manual, manual portal, languages |
| S07-N3-1 | replication | S07 | The company refreshed the design of its careers website in the spring. | careers website, careers site, website |

Term check passed: no detector term occurs in any base item or in the four filler training-day news items. The S07 detector deliberately excludes the bare word *careers*, which the 2026-06-03 filler item also uses.

## Per-variant tally

| log | variant | n | mentions | of which dismissed | tied base | flip \| mentioned | flip \| not mentioned | actions \| mentioned | actions \| not |
|---|---|---|---|---|---|---|---|---|---|
| rehearsal_borderline.jsonl | S03-N3-1 | 20 | 0 | 0 | 0 | – | 14/20 | – | {'sell': 13, 'hold': 6, 'buy': 1} |
| rehearsal_flat_momentum.jsonl | S01-N3-1 | 20 | 0 | 0 | 0 | – | 0/20 | – | {'buy': 20} |
| rehearsal_neg_momentum.jsonl | S01-N3-1 | 5 | 0 | 0 | 5 | – | – | – | {'sell': 3, 'hold': 1, 'buy': 1} |
| rehearsal_replication.jsonl | S04-N3-1 | 20 | 0 | 0 | 0 | – | 19/20 | – | {'buy': 18, 'sell': 1, 'hold': 1} |
| rehearsal_replication.jsonl | S05-N3-1 | 20 | 0 | 0 | 0 | – | 4/20 | – | {'hold': 16, 'buy': 4} |
| rehearsal_replication.jsonl | S06-N3-1 | 20 | 0 | 0 | 0 | – | 11/20 | – | {'buy': 8, 'hold': 9, 'sell': 3} |
| rehearsal_replication.jsonl | S07-N3-1 | 20 | 0 | 0 | 0 | – | 7/20 | – | {'sell': 13, 'hold': 7} |

## Pooled

- N3 rationales mentioning the distractor: 0 / 125
- Of those, rationales that also dismiss it as immaterial (regex, see script): 0
- Action differs from modal BASE, given mention: 0 / 0 (tied-baseline items excluded)
- Action differs from modal BASE, given no mention: 55 / 120

Pooling across logs and items is for legibility only; runs within an item are correlated and the registered analysis bootstraps items, not runs. No inference is drawn here.

## False-positive control

The same detector run over every non-N3 rationale of the same item. Those runs never saw the clause, so a hit is detector noise (or the model volunteering the topic unprompted).

| variant | control rows | hits |
|---|---|---|
| S01-N3-1 | 90 | 0 |
| S03-N3-1 | 110 | 0 |
| S04-N3-1 | 70 | 0 |
| S05-N3-1 | 70 | 0 |
| S06-N3-1 | 70 | 0 |
| S07-N3-1 | 70 | 0 |

## Comparison: does the rationale cite the filler memory items?

The memory holds four deliberately low-relevance training-day items. If the agent cites those, silence on the appended clause is a fact about the clause's position (appended to the decision-day item) rather than about low-relevance content in general.

| filler item | rationales citing it | of rows |
|---|---|---|
| investor-relations schedule (06-01) | 6 | 670 |
| registered office filing (06-02) | 158 | 670 |
| careers page openings (06-03) | 419 | 670 |
| industry directory entry (06-04) | 0 | 670 |

## Reading (exploratory, not a finding)

The appended clause is never named in any of the N3 rationales, while the filler memory items that FinMem presents as separate retrieved rows are named routinely. The plausible mechanism is positional: FinMem's prompt lists each retrieved memory row as its own numbered item and asks the model to reason over the list, so a low-relevance *row* is addressed and dismissed, whereas a low-relevance *sentence inside* the decision-day row is absorbed into that row's summary. Under that reading, any N3 movement the registered analysis finds is not the model reasoning about the distractor; it is the perturbation changing the row's surface form. That is consistent with N3's registered role as a null class, and it argues for reporting N3 and N1 movement on the same footing rather than treating N3 as the weaker manipulation. To be tested, not assumed: it would take a variant that inserts the distractor as its own memory row.

## Mentioning rationales, verbatim excerpts


