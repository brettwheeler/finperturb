# Session handoff — implement the three scoring rules (gaps list item 2)

Scope: **item 2 only.** Items 1 and 3–6 of the gaps list are out of scope; do not start them.
Item 2 is unblocked because it needs no fixtures, no `PARAPHRASE_API_KEY`, and no second engine.

---

## What this project is

FinPerturb tests whether a published LLM trading agent changes its buy/sell/hold decision
when a news item is reworded **without changing its meaning** — paraphrased (N1), renamed
(N2), or given an appended irrelevant sentence (N3). The agent is stochastic by design, so
the study first measures how often it disagrees **with itself** on identical input (the
decoding floor, φ) and reports every effect net of that. This repo is the **FinMem** arm
(arXiv 2311.13743); sibling repos will cover other engines.

The rules you are about to write are shared with the main study and with every future
engine. They exist so that two engines' numbers are comparable.

---

## Where things are

Host path: `C:\Users\brett\finperturb-finmem` (Windows). Everything executes in Docker.

```bash
# scoring / harness scripts (harness venv, no FinMem import)
docker run --rm --env-file C:\Users\brett\finperturb-finmem\.env -e FP_REQUIRE_KEYS=0 \
  -v C:\Users\brett\finperturb-finmem:/work -w /work finperturb-finmem:dev \
  python scoring/score_pilot.py --help
```

```bash
# anything importing FinMem's `puppy` package needs its own venv and cwd
docker run --rm --env-file C:\Users\brett\finperturb-finmem\.env -e FP_REQUIRE_KEYS=0 \
  -v C:\Users\brett\finperturb-finmem:/work -v finperturb-finmem_agent-venvs:/opt/venvs \
  -w /work/agents/finmem finperturb-finmem:dev poetry run python /work/harness/wrapper.py --help
```

`FP_REQUIRE_KEYS=0` is required because `PARAPHRASE_API_KEY` is still `REPLACE_ME`; the
entrypoint otherwise refuses to start. **No API calls are needed for this task** — scoring
reads only the logs.

| path | role |
|---|---|
| `scoring/score_pilot.py` | **the file you are changing** |
| `data/runs/*.jsonl` | append-only raw logs — never edit, never regenerate |
| `data/runs/pooled_flat_context_report.md` | current report; the others are stale |
| `harness/` | corpus builder, wrapper, runner, pre-flight checks |
| `agents/finmem` | upstream agent, pinned at `be814aa` — **never modify** |

---

## Ground rules (these are the experiment, not style)

- **The log is append-only.** Every correction lives in scoring code where a reader can see
  it. Do not rewrite, dedupe or "fix" a log.
- **The report presents; it never concludes.** No pass/fail, no thresholds-as-verdicts. The
  read-out rule is the project lead's, fixed before runs start.
- **Regenerable by one command** from the raw logs.
- **No silent caps.** Anything excluded is counted and named in the report.
- Do not modify `agents/finmem`.

---

## Evidence from the rehearsal (why each rule exists)

630 rows, 7 fabricated items, one frozen context, `gpt-5.4-mini-2026-03-17`, 0 errors.
These are rehearsal fixtures written by the analyst — **instrument-testing only, not
findings**.

Per-item φ (30 floor draws each): S01 0.064 · S02 0.500 · S03 0.638 · S04 0.444 ·
S05 0.278 · S06 0.460 · S07 0.444.

1. **Tie.** In the negative-momentum run, S01's BASE was `buy 2 / hold 1 / sell 2` — an exact
   tie, broken silently by `Counter.most_common` insertion order. Every flip rate for that
   item was then computed against an arbitrary winner. Worse, that item's FLOOR showed `buy`
   at 1-in-10, so the chosen baseline was a *rare* action and the variants "flipped" 5/5
   almost by construction.
2. **φ band.** At φ = 0.638 the modal flip rate put N3 at net +0.062 — indistinguishable from
   noise — while JSD with a permutation null gave p = 0.028. The flip rate structurally
   cannot measure a high-φ item, because its baseline is a coin flip.
3. **Permutation null.** `NULL_DRAWS = 2000`, seeds `RNG_SEED` and `+1/+2/+3`, and **no
   multiplicity correction anywhere**. The real grid is 20 items × 3 classes = 60 tests.

Also relevant: pooling the replication four with the other two items **reversed which class
had a CI excluding zero**. Intervals bootstrapped over 4–6 items are not trustworthy; the
rules must not encourage reading them as if they were.

---

## What to implement

### 2a — Modal tie rule

`baseline` is currently `Counter(base_actions[item]).most_common(1)[0][0]`.

- Detect an exact tie for top place. On a tie: **exclude the item from flip-rate scoring,
  retain it for distributional scoring.** Name the exclusion in the report with the item id
  and the tied counts.
- Add a **baseline margin** column to the baseline table: top-1 share minus top-2 share. A
  9-vs-8 split is not a tie but is just as arbitrary, and only the margin makes that visible.
- Excluded items must still appear in every JSD table.

### 2b — φ-band interpretability flag

Proposed design, **and it differs from the gaps-list wording on purpose** — raise it before
coding if the lead disagrees:

Rather than switching *which statistic governs* by band (which makes two engines'
headline numbers come from different statistics whenever their φ distributions differ),
keep **JSD + permutation null as primary everywhere** and mark the flip rate's
*interpretability*:

- flip rate is quotable when `φ < 0.20` **and** the baseline is not a tie;
- otherwise the report prints `not interpretable (φ = 0.46)` in place of the number.

The threshold must be a declared constant at the top of the file, not a literal buried in a
branch. On the rehearsal set only S01 would qualify — worth stating plainly in the report.

### 2c — Permutation null formalized

- `NULL_DRAWS` 2,000 → **10,000** for final runs (2,000 floors p-value resolution at 0.0005;
  our smallest observed was already reported as 0.000). Keep it a named constant and make it
  a CLI flag with the default at 10,000 so iteration stays fast.
- **Seed discipline:** one root seed, explicitly derived independent streams per analysis
  (currently ad-hoc `+1/+2/+3`). A report must be reproducible from the logs alone.
- **Multiplicity:** add Benjamini–Hochberg across the item × class grid; report raw and
  adjusted p side by side. Do not drop the raw values.
- Move the null machinery into its own module under `scoring/` with a docstring stating the
  procedure, so it is citable rather than being one session's ad-hoc analysis.

---

## Open decisions — confirm before coding

These are pre-registration calls and belong to the project lead, not to the implementer:

1. Tie handling: exclude (proposed) vs a declared tie-break.
2. φ threshold for flip-rate interpretability: 0.20 proposed.
3. Benjamini–Hochberg (proposed) vs Holm — BH controls FDR and suits a 60-cell screen; Holm
   is more conservative and controls FWER.
4. `NULL_DRAWS` final value: 10,000 proposed.
5. Whether 2b's reframing (interpretability flag, single governing statistic) is accepted in
   place of the band-switching rule as originally written.

---

## Things already in the file that should survive

- **Directional shift diagnostic.** Not in §7; added because JSD is direction-agnostic. It
  caught that the rehearsal's hand-written paraphrases pushed **+0.317 toward buy**
  consistently across items — the signature of drifted variants rather than agent
  instability. Do not remove it; it is the reason the rehearsal's "significant" results are
  correctly read as a fixture-quality alarm.
- **JSD's own floor.** The control is BASE vs FLOOR — the same text run as two separate
  blocks — so its divergence is pure sampling. Every variant JSD is reported net of it.
- **Context stamping.** Rows now carry a frozen-context stamp and the scorer refuses to pool
  logs whose contexts differ. All 630 existing rows predate the field and the report says so
  rather than assuming compatibility.
- **Marginal action distribution table**, which distinguishes a stable agent from one that
  answers the same way to everything.

---

## Verification

No API calls. Re-run against the pooled logs and confirm the unchanged quantities reproduce:

```bash
python scoring/score_pilot.py \
  --log data/runs/rehearsal_flat_momentum.jsonl data/runs/rehearsal_borderline.jsonl \
        data/runs/rehearsal_replication.jsonl \
  --manifest data/corpus/replication/manifest.json \
  --out data/runs/pooled_flat_context_report.md
```

Current values to reproduce: `phi = 0.4041` over 7 items; N1 net `+0.1156`
CI `[-0.0077, +0.2499]`; N3 net `+0.0924` CI `[+0.0085, +0.2007]`; 630 rows, 0 not-ok,
single model version.

Then confirm the new behaviour: no item in this pooled set has a tied baseline, so **build a
targeted check** rather than assuming the tie path works — the negative-momentum log
(`data/runs/rehearsal_neg_momentum.jsonl`, scored on its own, different frozen context) does
contain the S01 tie and is the natural test case.
