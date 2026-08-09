# FinPerturb — the FinAgent arm

**Status: cloned and pinned, no harness yet.** The engine is here; nothing runs.

| | |
|---|---|
| Paper | [arXiv 2402.18485](https://arxiv.org/abs/2402.18485) — A Multimodal Foundation Agent for Financial Trading (KDD 2024) |
| Upstream | https://github.com/DVampire/FinAgent |
| Pin | `17248a0b8b729ee3e093e30bb7bea7f52181f363` (cloned 2026-08-09) |
| Identification | **Established by source inspection, lead to confirm.** The README carries no citation, but the source matches the paper exactly: the module names (`market_intelligence`, `low_level_reflection`, `high_level_reflection` in `configs/exp/`) and the paper's six experiment assets (AAPL, AMZN, GOOGL, MSFT, TSLA, ETHUSD). No better-matching public repo was found (2026-08-09). |

The clone lives at `agents/finagent`, gitignored but pinned: its own `.git`
records the SHA above, and the engine is never modified — perturbations enter
through this arm's harness (when it exists), upstream code stays as published.

## Known frictions, recorded at clone time

- **Multimodal by design**: the market-intelligence module consumes charts as
  images. A text-only perturbation study has to establish what the visual
  channel contributes before φ on the text channel means anything — this joins
  the item-3 audit for this engine.
- Heavy dependency surface (FAISS via conda, Playwright with browser deps).
  Budget §3's one-to-two days.

## Before anything runs here (the gaps list, per-engine items)

- **Item 3 — perturbation-applicability audit**, per class, against the actual
  prompt-construction path (the FinMem N2 lesson: `puppy/prompts.py:16`).
- **Item 4 — memory-reset discipline** for its memory/trajectory state.
- **Item 6 — checkpoint parity**: quick-start end-to-end, then the
  extreme-headline sandbox check, before any φ measurement.

The harness, when built, mirrors `arms/finmem`'s shape: `harness/`, `data/`,
its own Dockerfile and compose project (own image, own venv volume, own `.env`).
Scoring is the repo root's `scoring/` — one copy, never per-arm.
