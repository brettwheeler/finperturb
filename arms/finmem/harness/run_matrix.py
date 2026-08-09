#!/usr/bin/env python3
"""§6: the run matrix, written to an append-only log, resumable by construction.

The log is the experiment's raw data and it is never edited (§8.4). Corrections
live in scoring code where a reader can see them. This script therefore only ever
opens the log with "a", writes whole lines, and flushes -- so a crash mid-matrix
loses at most the row in flight, and a rerun completes the gaps rather than
starting over.

RESUMABILITY is derived from the log itself rather than from a separate state
file, because a state file can disagree with the log and the log is the thing
that counts. On start, every (item, klass, variant, rep) that already has an "ok"
row is skipped. That makes the script safe to run repeatedly and safe to
interrupt, which matters when the alternative is an operator deciding by hand
which cells to redo.

WHAT COUNTS AS A CELL. FLOOR and BASE both send the base item's unmodified text:
FLOOR k times to measure the agent's disagreement with itself, BASE a few times
to establish the modal action a variant is compared against. They are separate
klasses in the log because they answer different questions, not because the
inputs differ -- and §7.1 depends on being able to tell them apart.

ERRORS are retried three times with backoff and then written as a row with
status "error" and an EMPTY action. §6.1 is explicit that an error message must
never occupy the action or rationale field, because a row that reads like a
decision will eventually be counted as one.
"""

from __future__ import annotations

import argparse
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from wrapper import AgentWrapper

RETRIES = 3
BACKOFF_BASE_S = 2.0

# FinMem sends model and messages only (chat.py:123), so nothing pins sampling
# and the provider's defaults apply -- which is §8.3's requirement, recorded here
# per row so the report can assert it rather than claim it.
DECODING_PARAMS = {
    "sent": {},
    "source": "finmem sends model+messages only (puppy/chat.py:123); provider defaults apply",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cell_key(item_id: str, klass: str, variant_id: Optional[str], rep: int) -> Tuple:
    return (item_id, klass, variant_id, rep)


def load_completed(log_path: Path) -> Set[Tuple]:
    """Which cells already have an 'ok' row.

    Malformed lines are skipped rather than fatal: a half-written final line from
    a killed process should cost that one cell, not the whole log.
    """
    done: Set[Tuple] = set()
    if not log_path.exists():
        return done
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("status") == "ok":
                done.add(cell_key(row["item_id"], row["klass"], row.get("variant_id"), row["rep"]))
    return done


def build_plan(manifest: Dict[str, Any], floor_k: int, base_reps: int, variant_reps: int) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    for cell in manifest["cells"]:
        common = {
            "cell_id": cell["cell_id"],
            "item_id": cell["item_id"],
            "variant_id": cell["variant_id"],
            "path": cell["path"],
            "text_sha256_16": cell["text_sha256_16"],
        }
        if cell["klass"] == "BASE":
            for rep in range(1, floor_k + 1):
                tasks.append({**common, "klass": "FLOOR", "rep": rep})
            for rep in range(1, base_reps + 1):
                tasks.append({**common, "klass": "BASE", "rep": rep})
        else:
            for rep in range(1, variant_reps + 1):
                tasks.append({**common, "klass": cell["klass"], "rep": rep})
    return tasks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    # 30, not §6.2's 10. Measured, not preferred: at k=10 the rehearsal put item
    # S01's floor at 0.18; at k=30 the same item came in at 0.064 with a 95% CI of
    # [0.000, 0.180]. The k=10 figure was not wrong, just badly resolved -- and it
    # is the number every reported flip rate is corrected by, and the number an
    # item is screened on. The extra 400 calls across 20 items cost about $1.
    parser.add_argument("--floor-k", type=int, default=30)
    # 20 apiece, not §6.2's 5, because the primary statistic changed. A flip rate
    # needs one number out of a cell (did it differ from the mode); a divergence
    # needs a DISTRIBUTION out of it, and five draws do not describe one. BASE
    # rises with the variants deliberately: JSD compares two estimated
    # distributions, so a precise variant measured against a noisy reference just
    # relocates the noise.
    parser.add_argument("--base-reps", type=int, default=20)
    parser.add_argument("--variant-reps", type=int, default=20)
    parser.add_argument(
        "--only-klass",
        nargs="+",
        choices=["FLOOR", "BASE", "N1", "N2", "N3"],
        help=(
            "run a subset of the matrix. The intended use is FLOOR first: phi is what "
            "decides whether an item can support a flip statistic at all, and an item "
            "whose floor distribution is near-uniform has a coin-flip baseline that no "
            "flip rate computed against it can mean anything. Screening on phi before "
            "spending on BASE and the variants protects the expensive part of the run."
        ),
    )
    args = parser.parse_args(argv)

    with (args.corpus / "manifest.json").open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    tasks = build_plan(manifest, args.floor_k, args.base_reps, args.variant_reps)

    # Deferred cells are counted and named. §8's objection to silent caps applies
    # here too: a log holding only FLOOR rows must be distinguishable from a
    # matrix that ran everything and found nothing.
    deferred: Dict[str, int] = {}
    if args.only_klass:
        keep = set(args.only_klass)
        for task in tasks:
            if task["klass"] not in keep:
                deferred[task["klass"]] = deferred.get(task["klass"], 0) + 1
        tasks = [t for t in tasks if t["klass"] in keep]

    done = load_completed(args.log)
    todo = [t for t in tasks if cell_key(t["item_id"], t["klass"], t["variant_id"], t["rep"]) not in done]

    # Count completions WITHIN this plan, not every ok row in the log. The log
    # accumulates across invocations, so len(done) reports cells this run was
    # never going to attempt and the three numbers stop adding up.
    already = len(tasks) - len(todo)

    run_id = uuid.uuid4().hex[:12]
    print(f"run_id {run_id}: {len(tasks)} cells planned, {already} already ok, {len(todo)} to run")
    if deferred:
        summary = ", ".join(f"{k}:{v}" for k, v in sorted(deferred.items()))
        print(f"  --only-klass {' '.join(sorted(args.only_klass))} deferred {summary}")
    if not todo:
        return 0

    wrapper = AgentWrapper(checkpoint=args.checkpoint, config_path=args.config)
    args.log.parent.mkdir(parents=True, exist_ok=True)

    # The frozen context, stamped on every row. Two runs are poolable only if they
    # share it: the same checkpoint (memory and price history), the same decision
    # date and the same price series. The rehearsal made this concrete -- the same
    # items under a falling tape gave phi 0.51 and under a flat one 0.28, so a
    # merge across contexts would average two different experiments and report the
    # mean as one.
    context = {
        "checkpoint_fingerprint": wrapper.checkpoint_fingerprint,
        "symbol": manifest["symbol"],
        "decision_date": manifest["decision_date"],
        "price_source": manifest.get("price_source", "UNDECLARED"),
        "train_days": manifest.get("train_days"),
    }
    print(f"  context {context['checkpoint_fingerprint']} @ {context['decision_date']}")

    counts: Dict[str, int] = {}
    with args.log.open("a", encoding="utf-8") as log:
        for index, task in enumerate(todo, start=1):
            decision = None
            for attempt in range(1, RETRIES + 1):
                decision = wrapper.decide(args.corpus / task["path"])
                if decision.status != "error":
                    break
                if attempt < RETRIES:
                    time.sleep(BACKOFF_BASE_S ** attempt)

            row = {
                "run_id": run_id,
                "ts": utc_now(),
                "item_id": task["item_id"],
                "variant_id": task["variant_id"],
                "klass": task["klass"],
                "rep": task["rep"],
                "cell_id": task["cell_id"],
                "text_sha256_16": task["text_sha256_16"],
                "action": decision.action,
                "weight": decision.weight,
                "rationale": decision.rationale,
                "model_version": decision.model_version,
                "context": context,
                "decoding_params": DECODING_PARAMS,
                "status": decision.status,
                "error": decision.error,
                "chat_calls": decision.chat_calls,
                "embedding_calls": decision.embedding_calls,
                "prompt_tokens": decision.prompt_tokens,
                "completion_tokens": decision.completion_tokens,
                "latency_s": decision.latency_s,
            }
            log.write(json.dumps(row, sort_keys=True) + "\n")
            log.flush()

            counts[decision.status] = counts.get(decision.status, 0) + 1
            print(
                f"[{index}/{len(todo)}] {task['cell_id']} {task['klass']} rep{task['rep']} -> "
                f"{decision.action or decision.status}",
                flush=True,
            )

    print(f"done: {counts}")
    print(f"log:  {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
