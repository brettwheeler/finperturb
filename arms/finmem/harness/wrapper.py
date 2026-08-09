#!/usr/bin/env python3
"""§5's seam: one FinMem decision, from a pristine checkpoint, with provenance.

    decide(corpus) -> Decision

A pure function of (corpus text, frozen context) plus the model's sampling noise.
It depends on nothing else -- not on prior calls, not on wall-clock, not on any
cache -- and the guarantees below are mechanical rather than aspirational.

RESET (§8.2). The guide suggests snapshotting the memory directory and copying it
back. Reading memorydb.py says something better is available: MemoryDB writes to
disk ONLY inside save_checkpoint. add_memory, decay, clean-up and memory jumps all
mutate an in-memory faiss index held on the object. So a fresh
LLMAgent.load_checkpoint builds an entirely new object graph from the pristine
files, and the previous call's memory goes out of scope. We simply never save.
The proof is enforced, not promised: the checkpoint's fingerprint is taken before
and after every decide() and a change raises.

...and copying would have been actively WRONG here. universe_index.pkl stores the
faiss index location as an ABSOLUTE path recorded at save time. Copy a checkpoint
elsewhere and load it, and faiss.read_index quietly reads the ORIGINAL file --
the same content while the original survives, and a crash or stale memory once it
does not. validate_checkpoint refuses to start when those paths have drifted.

PROVENANCE (§6.1). FinMem throws its response metadata away: parse_response
returns choices[0].message.content and nothing else (chat.py:60). model_version is
therefore unreachable through the agent's own code, so we intercept
httpx.Client.send -- which catches both the chat calls (httpx.post, chat.py:131)
and the embedding calls (the openai SDK, via langchain). Responses pass through
untouched; we only read them. agents/finmem stays byte-for-byte at be814aa.

NO CACHING (§8.7). Nothing here memoises a decision, and the interception layer
deliberately adds no cache of its own -- a proxy or response cache would collapse
the decoding floor toward zero and silently void §7.1.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import pickle
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

_AGENT_ROOT = Path(os.environ.get("FINMEM_ROOT", Path(__file__).resolve().parent.parent / "agents" / "finmem"))
if not (_AGENT_ROOT / "puppy").is_dir():
    raise SystemExit(f"cannot find FinMem's puppy package under {_AGENT_ROOT}; set FINMEM_ROOT")
sys.path.insert(0, str(_AGENT_ROOT))

from puppy import LLMAgent, MarketEnvironment, RunMode  # noqa: E402

CHAT_PATH = "/chat/completions"
EMBEDDING_PATH = "/embeddings"


# --------------------------------------------------------------------------
# provenance capture
# --------------------------------------------------------------------------


@dataclass
class CallRecord:
    url: str
    status_code: int
    model: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @property
    def is_chat(self) -> bool:
        return CHAT_PATH in self.url

    @property
    def is_embedding(self) -> bool:
        return EMBEDDING_PATH in self.url


class ResponseCapture:
    """Observe every HTTP response the agent's stack produces, and change none.

    httpx.Client.send rather than httpx.post: the chat path calls the module-level
    httpx.post, while embeddings go through the openai SDK's own client. Both
    funnel through Client.send, so one patch sees the whole call path -- which is
    what makes the per-decision call COUNT measurable, and that count is the
    multiplier on the entire run budget (§6.2).
    """

    def __init__(self) -> None:
        self.records: List[CallRecord] = []
        self._original = None

    def __enter__(self) -> "ResponseCapture":
        self._original = httpx.Client.send
        capture = self

        def send(client_self, request, **kwargs):
            response = capture._original(client_self, request, **kwargs)
            capture._record(str(request.url), response)
            return response

        httpx.Client.send = send
        return self

    def __exit__(self, *exc_info) -> None:
        httpx.Client.send = self._original

    def _record(self, url: str, response) -> None:
        record = CallRecord(url=url, status_code=response.status_code)
        # A failed call still belongs in the record -- §6.1 wants error rows
        # written honestly rather than dropped.
        if response.status_code == 200:
            with contextlib.suppress(Exception):
                body = response.json()
                record.model = body.get("model")
                usage = body.get("usage") or {}
                record.prompt_tokens = usage.get("prompt_tokens", 0) or 0
                record.completion_tokens = usage.get("completion_tokens", 0) or 0
                record.total_tokens = usage.get("total_tokens", 0) or 0
        self.records.append(record)

    def chat_model_version(self) -> Optional[str]:
        """The model that answered, asserted to be one model.

        §6.3 discards every row from a superseded version. Deciding that from the
        request would be a lie when the request names a floating alias; deciding
        it from the responses is the truth, and a split WITHIN one decision is a
        real fault rather than a curiosity.
        """
        models = {r.model for r in self.records if r.is_chat and r.model}
        if not models:
            return None
        if len(models) > 1:
            raise RuntimeError(f"one decision answered by multiple models: {sorted(models)}")
        return models.pop()


# --------------------------------------------------------------------------
# the decision
# --------------------------------------------------------------------------


@dataclass
class Decision:
    action: Optional[str]
    weight: Optional[float]
    rationale: str
    model_version: Optional[str]
    status: str
    error: Optional[str] = None
    chat_calls: int = 0
    embedding_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_s: float = 0.0
    decision_date: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def fingerprint(root: Path) -> str:
    """Cheap content fingerprint of the pristine checkpoint.

    Names, sizes and mtimes -- enough to catch a write, which is all this needs to
    do. Hashing a faiss index on every call would cost more than the guarantee is
    worth.
    """
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            digest.update(str(path.relative_to(root)).encode())
            digest.update(str(stat.st_size).encode())
            digest.update(str(int(stat.st_mtime)).encode())
    return digest.hexdigest()[:16]


def validate_checkpoint(checkpoint: Path) -> None:
    """Refuse to run against a checkpoint whose faiss indices have moved."""
    if not checkpoint.is_dir():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint}")

    universes = sorted(checkpoint.rglob("universe_index.pkl"))
    if not universes:
        raise RuntimeError(f"no memory layers under {checkpoint}; is this a FinMem checkpoint?")

    for universe_path in universes:
        with universe_path.open("rb") as handle:
            universe = pickle.load(handle)
        for symbol, record in universe.items():
            index_path = Path(record["index_save_path"])
            if not index_path.exists():
                raise RuntimeError(
                    f"{universe_path}: faiss index for {symbol} points at {index_path}, which does "
                    "not exist. universe_index.pkl stores ABSOLUTE paths, so a checkpoint cannot "
                    "be moved or copied -- rebuild it in place instead."
                )


class AgentWrapper:
    def __init__(self, checkpoint: Path, config_path: Path, agent_name: str = "agent_1") -> None:
        self.checkpoint = Path(checkpoint).resolve()
        self.config_path = Path(config_path).resolve()
        self.agent_name = agent_name
        validate_checkpoint(self.checkpoint)
        # Public: the runner stamps it on every row so logs from different frozen
        # contexts can never be pooled by accident. §6.3 already refuses to mix
        # model versions; the context deserves the same protection, and a
        # different checkpoint is a different experiment.
        self.checkpoint_fingerprint = fingerprint(self.checkpoint)
        self._fingerprint = self.checkpoint_fingerprint

    @staticmethod
    def _dedupe_log_handlers(agent) -> None:
        """LLMAgent.__init__ adds a FileHandler to a MODULE-level logger every time.

        Over a 1,100-call matrix that is 1,100 handlers on one logger, each line
        written 1,100 times, and an operational log that eats the disk. The agent
        is rebuilt per call by design, so the handlers have to be pruned per call
        too.
        """
        seen = set()
        for handler in list(agent.logger.handlers):
            key = getattr(handler, "baseFilename", id(handler))
            if key in seen:
                agent.logger.removeHandler(handler)
            else:
                seen.add(key)

    def decide(self, corpus_path: Path) -> Decision:
        corpus_path = Path(corpus_path)
        with corpus_path.open("rb") as handle:
            corpus = pickle.load(handle)
        days = sorted(corpus)

        started = time.monotonic()
        with ResponseCapture() as capture:
            try:
                # Fresh agent from the pristine checkpoint. THIS is the reset.
                agent = LLMAgent.load_checkpoint(path=str(self.checkpoint / self.agent_name))
                self._dedupe_log_handlers(agent)

                environment = MarketEnvironment(
                    symbol=agent.trading_symbol,
                    env_data_pkl=corpus,
                    start_date=days[0],
                    end_date=days[-1],
                )
                market_info = environment.step()
                if market_info[-1]:
                    raise RuntimeError("corpus terminated before its only step")
                decision_date: date = market_info[0]

                agent.step(market_info=market_info, run_mode=RunMode.Test)
                result = agent.reflection_result_series_dict.get(decision_date) or {}
                action = result.get("investment_decision")
                rationale = result.get("summary_reason", "") or ""
                status = "ok" if action else "no_decision"
                error = None if action else "reflection produced no investment_decision"
            except Exception as exc:  # noqa: BLE001 - the row must be written either way
                # §6.1: never store an error message in the action or rationale
                # fields as if it were output. It goes in `error`, and action stays
                # empty, so a failed call can never be mistaken for a hold.
                return self._finish(
                    capture,
                    started,
                    action=None,
                    rationale="",
                    status="error",
                    error=f"{type(exc).__name__}: {exc}",
                    decision_date=None,
                )

        after = fingerprint(self.checkpoint)
        if after != self._fingerprint:
            raise RuntimeError(
                "the pristine checkpoint changed during decide(); memory is leaking "
                "between calls and every downstream number is void (§8.2)"
            )

        return self._finish(
            capture,
            started,
            action=action,
            rationale=rationale,
            status=status,
            error=error,
            decision_date=decision_date.isoformat(),
        )

    @staticmethod
    def _finish(capture, started, *, action, rationale, status, error, decision_date) -> Decision:
        try:
            model_version = capture.chat_model_version()
        except RuntimeError as exc:
            model_version, status, error = None, "error", str(exc)
        return Decision(
            action=action,
            # FinMem emits a direction, never a size (__process_test_action maps
            # buy/hold/else to +1/0/-1), so weight is structurally absent here
            # rather than merely unrecorded.
            weight=None,
            rationale=rationale,
            model_version=model_version,
            status=status,
            error=error,
            chat_calls=sum(1 for r in capture.records if r.is_chat),
            embedding_calls=sum(1 for r in capture.records if r.is_embedding),
            prompt_tokens=sum(r.prompt_tokens for r in capture.records),
            completion_tokens=sum(r.completion_tokens for r in capture.records),
            latency_s=round(time.monotonic() - started, 3),
            decision_date=decision_date,
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", type=Path, required=True, help="pristine checkpoint dir (never written)")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True, help="a single cell pickle")
    parser.add_argument("--repeat", type=int, default=1, help="reps on the same cell; the floor is measured this way")
    args = parser.parse_args(argv)

    wrapper = AgentWrapper(checkpoint=args.checkpoint, config_path=args.config)
    for _ in range(args.repeat):
        print(json.dumps(wrapper.decide(args.corpus).as_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
