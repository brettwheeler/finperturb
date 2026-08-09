#!/usr/bin/env python3
"""§5.3's three gates. All three must pass before any real run.

RESET      decide() on one focal cell ten times, interleaved with other cells.
           The focal action distribution must not drift with position. Drift means
           state is leaking between calls, which makes an agent look stable
           because it remembers its own previous answer -- the exact false
           negative this study exists to avoid (§8.2).

SANITY     one extreme negative and one extreme positive headline. The agent must
           react differently. If it does not, either the injection point is dead
           (the agent never sees the text) or the agent genuinely ignores input.
           Those need opposite responses and §5.3 says escalate rather than guess,
           so this reports and refuses to conclude.

VERSION    model_version present and identical across every call. §6.3 discards
           rows from a superseded version; that rule is worthless if the field is
           empty or drifts unnoticed.

A NOTE ON POWER, because it would be dishonest to omit it: ten focal draws split
into halves is a weak instrument. It catches gross leakage -- a first half of
"buy" turning into a second half of "hold" -- and nothing subtler. It is a smoke
test, not the floor estimate; §7.1's phi is what quantifies the agent's own
variability, and it uses the full matrix.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from wrapper import AgentWrapper, Decision


def cell_path(corpus_root: Path, cell_id: str) -> Path:
    with (corpus_root / "manifest.json").open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    for cell in manifest["cells"]:
        if cell["cell_id"] == cell_id:
            return corpus_root / cell["path"]
    raise SystemExit(f"cell {cell_id!r} not in {corpus_root}/manifest.json")


def run_reset_test(wrapper: AgentWrapper, focal: Path, distractors: List[Path], reps: int):
    """Interleave so that a leak would show up as drift rather than as noise.

    The distractors matter: repeating the focal cell alone would let a leak look
    like consistency. Sandwiching other items between repeats means a leaking
    agent has something DIFFERENT to remember each time.
    """
    focal_results: List[Decision] = []
    everything: List[Decision] = []
    for i in range(reps):
        decision = wrapper.decide(focal)
        focal_results.append(decision)
        everything.append(decision)
        everything.append(wrapper.decide(distractors[i % len(distractors)]))

    actions = [d.action for d in focal_results]
    half = len(actions) // 2
    first, second = Counter(actions[:half]), Counter(actions[half:])
    return {
        "sequence": actions,
        "first_half": dict(first),
        "second_half": dict(second),
        "drifted": first != second,
    }, everything


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True, help="smoke corpus root")
    parser.add_argument("--sanity-corpus", type=Path, required=True)
    parser.add_argument("--focal", default="S01__BASE")
    parser.add_argument("--distractors", nargs="+", default=["S02__BASE", "S01__N1__S01-N1-1"])
    parser.add_argument("--reps", type=int, default=10)
    # Arm-anchored, not /work-anchored: since the monorepo, /work is the repo
    # root, and this harness belongs to one arm however it is invoked.
    parser.add_argument(
        "--log",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "logs" / "wrapper_verification.jsonl",
    )
    args = parser.parse_args(argv)

    wrapper = AgentWrapper(checkpoint=args.checkpoint, config_path=args.config)

    focal = cell_path(args.corpus, args.focal)
    distractors = [cell_path(args.corpus, name) for name in args.distractors]

    print(f"RESET: {args.reps} focal calls interleaved with {len(distractors)} distractors...")
    reset, decisions = run_reset_test(wrapper, focal, distractors, args.reps)

    print("SANITY: one extreme negative, one extreme positive...")
    negative = wrapper.decide(cell_path(args.sanity_corpus, "SANITY-NEG__BASE"))
    positive = wrapper.decide(cell_path(args.sanity_corpus, "SANITY-POS__BASE"))
    decisions.extend([negative, positive])

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a", encoding="utf-8") as handle:
        for decision in decisions:
            handle.write(json.dumps(decision.as_dict(), sort_keys=True) + "\n")

    versions = {d.model_version for d in decisions}
    errors = [d for d in decisions if d.status != "ok"]

    print()
    print("=" * 68)
    reset_ok = not reset["drifted"]
    print(f"RESET   {'PASS' if reset_ok else 'FLAG'}")
    print(f"        sequence:    {reset['sequence']}")
    print(f"        first half:  {reset['first_half']}")
    print(f"        second half: {reset['second_half']}")
    if not reset_ok:
        print("        distributions differ by position -- inspect before running anything (§8.2)")

    sanity_ok = negative.action != positive.action and negative.action and positive.action
    print(f"SANITY  {'PASS' if sanity_ok else 'FAIL'}")
    print(f"        extreme negative -> {negative.action}")
    print(f"        extreme positive -> {positive.action}")
    if not sanity_ok:
        print("        SAME ACTION FOR BOTH POLES. Either the injection point is dead or the")
        print("        agent ignores its input. §5.3: escalate to the project lead, do not")
        print("        diagnose this alone.")

    version_ok = len(versions) == 1 and None not in versions
    print(f"VERSION {'PASS' if version_ok else 'FAIL'}")
    print(f"        versions seen: {sorted(v or 'None' for v in versions)}  across {len(decisions)} calls")

    chat = sum(d.chat_calls for d in decisions)
    embed = sum(d.embedding_calls for d in decisions)
    prompt = sum(d.prompt_tokens for d in decisions)
    completion = sum(d.completion_tokens for d in decisions)
    print("-" * 68)
    print(f"{len(decisions)} decisions | {chat} chat + {embed} embedding calls")
    print(f"tokens: {prompt} prompt, {completion} completion")
    print(f"errors: {len(errors)}")
    print(f"log:    {args.log}")
    print("=" * 68)

    return 0 if (reset_ok and sanity_ok and version_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
