#!/usr/bin/env python3
"""Check a built corpus against FinMem's OWN environment, not against our idea of it.

build_corpus.py validates the shape it believes MarketEnvironment wants. This
runs the real class -- same pydantic model, same step() arithmetic, same
termination rule -- so a schema drift between the agent and the builder is caught
here rather than 400 calls into a run matrix.

Must run in FinMem's venv (it imports puppy), which is why it is invoked through
poetry from agents/finmem rather than with the harness interpreter.

Three things are asserted per cell, and each has a specific failure in mind:

  exactly one step   a corpus that steps twice would decide twice and log one
                     row, and the second decision would carry the first one's
                     news in memory
  the text arrives   proves the injection point is live. §5.3's sanity-reaction
                     test exists because a dead injection point looks exactly
                     like an agent that ignores its input
  then terminates    a corpus that never terminates hangs the runner
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List

# puppy is imported from the cloned agent, which is not installed as a package --
# poetry installs its dependencies with --no-root. sys.path[0] is THIS script's
# directory, so the agent root has to be added explicitly; resolving it from
# __file__ rather than the cwd means the script works however it is invoked.
_AGENT_ROOT = Path(os.environ.get("FINMEM_ROOT", Path(__file__).resolve().parent.parent / "agents" / "finmem"))
if not (_AGENT_ROOT / "puppy").is_dir():
    raise SystemExit(f"cannot find FinMem's puppy package under {_AGENT_ROOT}; set FINMEM_ROOT")
sys.path.insert(0, str(_AGENT_ROOT))

from puppy import MarketEnvironment  # noqa: E402  (path set up above)


def load_corpus(path: Path) -> Dict[Any, Any]:
    with path.open("rb") as handle:
        return pickle.load(handle)


def check_cell(root: Path, cell: Dict[str, Any], symbol: str) -> List[str]:
    problems: List[str] = []
    corpus = load_corpus(root / cell["path"])
    days = sorted(corpus)

    if len(days) != 2:
        problems.append(f"{cell['cell_id']}: expected 2 dates, found {len(days)}")
        return problems

    env = MarketEnvironment(
        symbol=symbol,
        env_data_pkl=corpus,
        start_date=days[0],
        end_date=days[-1],
    )
    if env.simulation_length != 1:
        problems.append(f"{cell['cell_id']}: simulation_length {env.simulation_length}, expected 1")

    cur_date, cur_price, filing_k, filing_q, news, record, done = env.step()
    if done:
        problems.append(f"{cell['cell_id']}: terminated before its only step")
        return problems
    if cur_date != days[0]:
        problems.append(f"{cell['cell_id']}: stepped {cur_date}, expected {days[0]}")
    if not isinstance(news, list):
        problems.append(f"{cell['cell_id']}: news is {type(news).__name__}, expected list")
    elif len(news) != 1:
        problems.append(f"{cell['cell_id']}: {len(news)} news items, expected 1")
    if filing_k is not None or filing_q is not None:
        problems.append(f"{cell['cell_id']}: filings present; decision context should carry none")
    if cur_price is None or cur_price <= 0:
        problems.append(f"{cell['cell_id']}: bad price {cur_price!r}")
    if record is None:
        # Discarded in test mode, but step() computes it from the second date's
        # price -- a None here means that price is missing and train mode would break.
        problems.append(f"{cell['cell_id']}: cur_record is None; the second date has no usable price")

    if not env.step()[-1]:
        problems.append(f"{cell['cell_id']}: did not terminate after one step")

    return problems


def check_train(root: Path, manifest: Dict[str, Any], symbol: str, minimum: int) -> List[str]:
    problems: List[str] = []
    corpus = load_corpus(root / manifest["train_pickle"])
    days = sorted(corpus)

    if len(days) < minimum:
        problems.append(
            f"train.pkl: {len(days)} dates, needs >= {minimum} or Portfolio.get_moment(3) "
            "is None at decision time and every prompt loses its momentum line"
        )

    env = MarketEnvironment(symbol=symbol, env_data_pkl=corpus, start_date=days[0], end_date=days[-1])
    steps = 0
    while True:
        info = env.step()
        if info[-1]:
            break
        steps += 1
    if steps != len(days) - 1:
        problems.append(f"train.pkl: stepped {steps} times, expected {len(days) - 1}")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    parser.add_argument("--min-train-days", type=int, default=4)
    args = parser.parse_args(argv)

    root = args.corpus
    with (root / "manifest.json").open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    symbol = manifest["symbol"]

    problems = check_train(root, manifest, symbol, args.min_train_days)
    for cell in manifest["cells"]:
        problems.extend(check_cell(root, cell, symbol))

    if problems:
        print(f"FAILED ({len(problems)} problems)", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(f"corpus OK: train.pkl + {len(manifest['cells'])} cells, symbol {symbol}")
    print(f"  decision date {manifest['decision_date']}, price source: {manifest['price_source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
