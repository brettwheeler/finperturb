# FinPerturb — the TradingAgents arm

**Status: cloned and pinned, no harness yet.** The engine is here; nothing runs.

| | |
|---|---|
| Paper | [arXiv 2412.20138](https://arxiv.org/abs/2412.20138) — TradingAgents: Multi-Agents LLM Financial Trading Framework |
| Upstream | https://github.com/TauricResearch/TradingAgents |
| Pin | `a33fd4c0f134485a43553a2c23a63cb14adbd88f` (cloned 2026-08-09) |
| Identification | **Official** — the repo carries the paper's arXiv badge and citation block |

The clone lives at `agents/tradingagents`, gitignored but pinned: its own `.git`
records the SHA above, and the engine is never modified — perturbations enter
through this arm's harness (when it exists), upstream code stays as published.

## Before anything runs here (the gaps list, per-engine items)

- **Item 3 — perturbation-applicability audit.** Read the prompt-construction
  path and record, per class, whether the perturbation survives into the prompt
  intact. The specific question: does any analyst role inject the ticker,
  company name, or price context independently of the news text? (FinMem failed
  N2 on exactly this — `puppy/prompts.py:16`.)
- **Item 4 — memory-reset discipline.** The debate scaffold holds conversation
  history and agent memories; §5.1's no-run-remembers-siblings requirement needs
  a verified reset mechanism for this architecture before any variant run.
- **Item 6 — checkpoint parity.** README quick-start end-to-end, then the
  extreme-headline sandbox check, before any φ measurement.

The harness, when built, mirrors `arms/finmem`'s shape: `harness/`, `data/`,
its own Dockerfile and compose project (own image, own venv volume, own `.env`).
Scoring is the repo root's `scoring/` — one copy, never per-arm.
