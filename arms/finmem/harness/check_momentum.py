#!/usr/bin/env python3
"""Pre-flight: what momentum will the frozen context actually present?

This exists because of a measured result, not a hunch. The same fixtures under a
rising price series returned buy 20/20 (phi = 0); under a falling one they went
sell/hold with phi = 0.51. The momentum sign is not background detail, it is the
single most influential thing in the frozen context -- so it gets verified before
a matrix runs rather than inferred afterwards from rationales.

Three states, and the third is easy to miss:

    +1 / -1   reflection.py:228 appends "The cumulative return of past 3 days for
              this stock is <positive|negative>."
     0        reflection.py:347 guards with `if momentum:`, and 0 is falsy in
              Python -- so the momentum explanation is dropped ENTIRELY rather
              than stated as zero. That makes flat the most neutral context
              available, but only if it is exactly zero.

Exactness matters: get_moment sums float diffs and branches on `> 0` / `< 0`, so
a cent of rounding turns an intended flat context into a directional one, and
nothing in the log would ever say so.

Reads the checkpoint's portfolio into memory and mutates only that copy; the
checkpoint on disk is never written.
"""

from __future__ import annotations

import argparse
import os
import pickle
import sys
from datetime import date
from pathlib import Path

_AGENT_ROOT = Path(os.environ.get("FINMEM_ROOT", Path(__file__).resolve().parent.parent / "agents" / "finmem"))
if not (_AGENT_ROOT / "puppy").is_dir():
    raise SystemExit(f"cannot find FinMem's puppy package under {_AGENT_ROOT}; set FINMEM_ROOT")
sys.path.insert(0, str(_AGENT_ROOT))

import puppy  # noqa: F401,E402  (registers the classes the checkpoint unpickles into)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--cell", type=Path, required=True, help="a decision cell pickle, for its price")
    parser.add_argument("--agent-name", default="agent_1")
    parser.add_argument("--window", type=int, default=3)
    parser.add_argument("--expect", choices=["1", "0", "-1"], help="fail if the momentum differs")
    args = parser.parse_args(argv)

    with (args.checkpoint / args.agent_name / "state_dict.pkl").open("rb") as handle:
        portfolio = pickle.load(handle)["portfolio"]

    with args.cell.open("rb") as handle:
        corpus = pickle.load(handle)
    decision_day = sorted(corpus)[0]
    symbol = next(iter(corpus[decision_day]["price"]))
    decision_price = corpus[decision_day]["price"][symbol]

    print(f"trained price series: {list(portfolio.market_price_series)}")
    print(f"day_count after training: {portfolio.day_count}")

    portfolio.update_market_info(new_market_price_info=decision_price, cur_date=decision_day)
    result = portfolio.get_moment(moment_window=args.window)

    if result is None:
        print(f"momentum: None (day_count {portfolio.day_count} <= window {args.window})")
        print("  the prompt will instruct the model to consider momentum and supply none")
        return 1

    moment = result["moment"]
    print(f"decision price {decision_price} on {decision_day}")
    print(f"momentum: {moment:+d}")
    if moment == 0:
        print("  -> `if momentum:` is falsy; the momentum block is OMITTED from the prompt")
    else:
        direction = "positive" if moment > 0 else "negative"
        print(f'  -> prompt will state: "The cumulative return of past 3 days for this stock is {direction}."')

    if args.expect is not None and moment != int(args.expect):
        print(f"FAIL: expected {args.expect}, got {moment}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
