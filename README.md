# FinPerturb

Does a published LLM trading agent change its buy/sell/hold decision when the
news is reworded **without changing its meaning**? Paraphrased (N1), renamed
(N2), or given an appended irrelevant sentence (N3). The agent is stochastic by
design, so the study first measures how often it disagrees with itself on
identical input (the decoding floor, φ) and reports every effect net of that.

## Layout

```
scoring/          the pre-registered scoring rules — ONE copy, every arm
arms/
  finmem/         FinMem        (arXiv 2311.13743) — the working arm
  tradingagents/  TradingAgents (arXiv 2412.20138) — cloned + pinned, no harness yet
  finagent/       FinAgent      (arXiv 2402.18485) — cloned + pinned, no harness yet
docs/             session handoffs and study notes
```

**One repo, one arm per engine** (converted from repo-per-arm on 2026-08-09).
Each arm is self-contained below its own directory — its Dockerfile, image,
compose project, named venv volume, `data/runs/` and `.env` — because the thing
that genuinely cannot be shared is the dependency set: FinMem pins Python
`>=3.10,<3.11` and a 2024-era stack, and each sibling pins something else. What
IS shared is `scoring/`, and sharing it as one directory in one tree is the
point of the monorepo: the pre-registered rules cannot drift between arms
because there is exactly one copy, and "both engines were scored under the same
rules" is answered by the repo SHA each report prints in its *Scoring rules in
force* table.

There is deliberately **no shared harness and no engine switch**. Whether a
perturbation class is even *valid* is per-engine (N2 died for FinMem because
`puppy/prompts.py:16` states the ticker independently of the news), so each
arm's harness names its engine in its own code, and a log row's provenance is
never an environment variable.

## Running

Scoring runs from the repo root, against any arm's logs:

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v C:\Users\brett\finperturb:/work -w /work finperturb-finmem:dev python scoring/score_pilot.py --log arms/finmem/data/runs/<run>.jsonl --out arms/finmem/data/runs/<report>.md
```

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v C:\Users\brett\finperturb:/work -w /work finperturb-finmem:dev python -m pytest scoring/test_scoring_rules.py -q
```

Agent and harness work happens inside the arm — see each arm's own README.
`docker compose` from an arm's directory mounts this whole repo at `/work` and
starts you in the arm.

## Upstream engine clones

Each arm vendors its engine under `arms/<arm>/agents/<engine>` as an ordinary
clone, **gitignored but pinned**: the clone's own `.git` records the pin, the
arm's README states it, and the engine is never modified — perturbations enter
through each arm's harness, upstream code stays as published.
