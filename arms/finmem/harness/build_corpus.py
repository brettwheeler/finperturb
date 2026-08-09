#!/usr/bin/env python3
"""Turn frozen fixtures into FinMem-shaped environment pickles.

This is the whole of §5.2.1 ("inject at the data layer, not the prompt") and it
needs no change to the agent: FinMem's MarketEnvironment takes a pickle of
    Dict[date, {"price": {sym: float},
                "filing_k": {sym: str}, "filing_q": {sym: str},
                "news": {sym: [str, ...]}}]
so substituting fixture text is a matter of writing that dict. agents/finmem
stays byte-for-byte at be814aa, which is what keeps the experiment's claim about
the published agent rather than about our edit of it.

TWO KINDS OF CORPUS, and they exist for different reasons.

  TRAINING (one pickle, several dates) mints the checkpoint that test mode
  requires -- run.py refuses to run test without -tap. It is NOT part of the
  measurement: train mode hands the agent the next day's price move and sets the
  action to sign(future_return), so nothing it "decides" is a decision.

  DECISION (one pickle per cell, exactly two dates) is one measurable call. Two
  dates because MarketEnvironment.step() reads date_series[0] as future_date and
  simulation_length is len(dates) - 1 -- so a 2-date pickle steps the agent
  exactly once and then terminates. One decision per file, which is what makes
  the run matrix's cells addressable and its restarts resumable.

WHY MIN_TRAIN_DAYS IS 4 AND NOT 2. Portfolio.get_moment(3) answers None while
day_count <= 3, and day_count is restored from the checkpoint. Train over two
days and every test prompt silently loses its momentum line -- the prompt still
instructs the model to "consider the momentum of the historical stock price",
and there is nothing there. A malformed prompt shared by every cell would not
show up as an error anywhere; it would just quietly change what is being
measured.

Deterministic by construction: no clock, no randomness, sorted iteration. The
same fixtures and config produce byte-identical pickles, so a corpus can be
rebuilt and compared rather than trusted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set

# Portfolio.get_moment(moment_window=3) needs day_count > 3, and day_count comes
# off the restored checkpoint plus the one update the decision step itself makes.
MIN_TRAIN_DAYS = 4

# FinMem writes the whole news list into short memory for the date. One element,
# so the fixture text is the only thing competing for the model's attention and a
# flip cannot be attributed to a neighbour headline.
DECISION_NEWS_ITEMS = 1

BUILDER_VERSION = "1"


class CorpusError(Exception):
    """A fixture or config problem, raised at build time rather than at run time."""


# --------------------------------------------------------------------------
# record construction
# --------------------------------------------------------------------------


def day_record(
    symbol: str,
    price: float,
    news: Sequence[str] = (),
    filing_k: str | None = None,
    filing_q: str | None = None,
) -> Dict[str, Any]:
    """One date's row, in the exact shape MarketEnvironment validates.

    news is ALWAYS a list, even when empty. FinMem substitutes {symbol: ''} -- a
    bare string, not a list -- when the news dict is empty (environment.py:85),
    and _handling_news then passes that string where a list is expected. It is a
    latent bug in the agent; we simply never hand it the input that triggers it.

    Filings are omitted as {} rather than as empty strings: step() treats a
    zero-length dict as "no filing" and indexes by symbol otherwise, so an empty
    string would be written into memory as a real, blank 10-K.
    """
    if price <= 0:
        # Portfolio.update_market_info validates price > 0 via pydantic, and it
        # does so mid-run, after the API calls for that step have been paid for.
        raise CorpusError(f"price must be > 0, got {price!r}")

    record: Dict[str, Any] = {
        "price": {symbol: float(price)},
        "filing_k": {symbol: filing_k} if filing_k else {},
        "filing_q": {symbol: filing_q} if filing_q else {},
        "news": {symbol: [str(n) for n in news]},
    }
    validate_record(record, symbol)
    return record


def validate_record(record: Dict[str, Any], symbol: str) -> None:
    """Mirror of environment.OneDateRecord, applied to EVERY date.

    FinMem validates only the first date (environment.py:42), so a malformed row
    in the middle of a corpus surfaces as a TypeError deep in a run. Checking all
    of them here costs nothing and moves the failure to build time.
    """
    for key in ("price", "filing_k", "filing_q", "news"):
        if key not in record:
            raise CorpusError(f"record missing {key!r}")
        if not isinstance(record[key], dict):
            raise CorpusError(f"{key!r} must be a dict, got {type(record[key]).__name__}")

    if symbol not in record["price"]:
        raise CorpusError(f"price has no entry for {symbol!r}")
    if not isinstance(record["price"][symbol], float):
        raise CorpusError("price must be a float")
    if symbol not in record["news"]:
        raise CorpusError(f"news has no entry for {symbol!r}")
    if not isinstance(record["news"][symbol], list):
        raise CorpusError("news must be a list of strings")
    if not all(isinstance(n, str) for n in record["news"][symbol]):
        raise CorpusError("news entries must be strings")


def validate_corpus(corpus: Dict[date, Dict[str, Any]], symbol: str, *, minimum: int) -> None:
    if len(corpus) < minimum:
        raise CorpusError(f"corpus has {len(corpus)} dates, needs at least {minimum}")
    for key in corpus:
        if not isinstance(key, date):
            raise CorpusError(f"corpus keys must be datetime.date, got {type(key).__name__}")
    for day in sorted(corpus):
        validate_record(corpus[day], symbol)


# --------------------------------------------------------------------------
# the two builders
# --------------------------------------------------------------------------


def build_training_corpus(
    symbol: str,
    prices: Dict[date, float],
    news_by_date: Dict[date, Sequence[str]] | None = None,
) -> Dict[date, Dict[str, Any]]:
    """The checkpoint-minting corpus.

    News defaults to empty on every date, which is §5.2.2's "empty-but-initialized
    memory state" taken literally: the agent ends up with a working portfolio and
    price history but almost nothing in short memory, so the decision under test
    rests on the fixture text rather than on retrieved neighbours.

    Supplying news_by_date is the other arm -- a deliberately stocked memory --
    and it is a different experiment, not a better-configured version of this one.
    """
    news_by_date = news_by_date or {}
    if len(prices) < MIN_TRAIN_DAYS:
        raise CorpusError(
            f"training needs at least {MIN_TRAIN_DAYS} dates so Portfolio.get_moment(3) "
            f"is defined at decision time; got {len(prices)}"
        )

    # EVERY training date needs news, and this is not a preference.
    # _handling_news forwards whatever it gets, and `[] != {}` is True in Python
    # (agent.py:180), so an empty list reaches MemoryDB.add_memory, embeds to a
    # zero-length array, and dies in faiss.normalize_L2 with
    # "IndexError: tuple index out of range" -- verified, not assumed. The
    # symmetric trap is an empty news DICT, which environment.py:85 turns into a
    # bare '' and embeds as an empty string.
    #
    # Note this is only the WRITE path. Retrieval tolerates an unseen symbol
    # perfectly well (MemoryDB.query returns [], []), so "empty-but-initialized"
    # was never going to fail at read time -- which is exactly why this would
    # have surfaced as a crash mid-training rather than as a bad decision.
    missing = [day for day in sorted(prices) if not news_by_date.get(day)]
    if missing:
        raise CorpusError(
            f"training dates {[d.isoformat() for d in missing]} have no news; FinMem "
            "crashes on empty news. Supply neutral, decision-irrelevant text via "
            "config 'training_news'."
        )

    corpus = {
        day: day_record(symbol, prices[day], news=news_by_date.get(day, ()))
        for day in sorted(prices)
    }
    validate_corpus(corpus, symbol, minimum=MIN_TRAIN_DAYS)
    return corpus


def build_decision_corpus(
    symbol: str,
    text: str,
    decision_date: date,
    next_date: date,
    decision_price: float,
    next_price: float,
) -> Dict[date, Dict[str, Any]]:
    """One measurable call: the fixture text on decision_date, nothing else.

    next_date carries a price and no news. It is never stepped -- the loop breaks
    on it -- but MarketEnvironment.step computes cur_record as
    future_price - cur_price before returning, so the price has to be there. In
    test mode that record is discarded (agent.py:579); it is the arithmetic that
    needs it, not the agent.
    """
    if next_date <= decision_date:
        raise CorpusError(f"next_date {next_date} must fall after decision_date {decision_date}")
    if not text.strip():
        raise CorpusError("decision text is empty")

    corpus = {
        decision_date: day_record(symbol, decision_price, news=[text]),
        next_date: day_record(symbol, next_price, news=()),
    }
    validate_corpus(corpus, symbol, minimum=2)
    return corpus


# --------------------------------------------------------------------------
# fixtures -> cells
# --------------------------------------------------------------------------


def text_digest(text: str) -> str:
    """Ties a logged row back to the exact bytes that produced it.

    §8.6 freezes the fixtures; this is what makes that checkable rather than
    promised. A corpus rebuilt from edited fixtures announces itself as a changed
    digest instead of quietly running different inputs under the same cell id.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_json(path: Path) -> Any:
    if not path.exists():
        raise CorpusError(f"missing fixture file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


NUMERIC = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numeric_tokens(text: str) -> Set[str]:
    """Every number in the text, comma-stripped so 1,200 and 1200 compare equal."""
    return {match.group(0).replace(",", "").rstrip(".") for match in NUMERIC.finditer(text)}


def check_numbers_preserved(base_text: str, variant: Dict[str, Any]) -> None:
    """§4.2's number check, as a build-time gate.

    It belongs in gen_variants.py, where a failed check means reject-and-retry
    against the paraphrase provider. That script does not exist yet, so right now
    nothing anywhere verifies that a paraphrase kept its figures -- and a variant
    that quietly dropped "18.4%" is not a meaning-preserving rewrite, it is a
    different news item that will flip the decision for an honest reason and be
    counted as instability.

    Subset, not equality: N3 appends a sentence that may introduce new numbers,
    and that is the class working as designed.
    """
    missing = numeric_tokens(base_text) - numeric_tokens(variant["text"])
    if missing:
        raise CorpusError(
            f"variant {variant['id']!r} ({variant['klass']}) drops numbers present in base "
            f"{variant['base_id']!r}: {sorted(missing)}. A variant is never hand-patched (§4.3) -- "
            "regenerate it."
        )


def collect_cells(fixtures_dir: Path) -> List[Dict[str, Any]]:
    """Every text that will be run, as (cell_id, klass, text).

    BASE and the three variant classes are collected together because they are
    the same kind of thing downstream -- one text, one pickle, N reps. FLOOR is
    absent on purpose: it re-runs the BASE pickle and needs no corpus of its own.
    """
    base_items = load_json(fixtures_dir / "base_items.json")
    cells: List[Dict[str, Any]] = []

    for item in base_items:
        item_id = item["id"]
        cells.append(
            {
                "cell_id": f"{item_id}__BASE",
                "item_id": item_id,
                "variant_id": None,
                "klass": "BASE",
                "text": item["text"],
            }
        )

    variants_path = fixtures_dir / "variants.json"
    if variants_path.exists():
        known = {item["id"]: item["text"] for item in base_items}
        for variant in load_json(variants_path):
            base_id = variant["base_id"]
            if base_id not in known:
                raise CorpusError(f"variant {variant['id']!r} names unknown base item {base_id!r}")
            check_numbers_preserved(known[base_id], variant)
            cells.append(
                {
                    "cell_id": f"{base_id}__{variant['klass']}__{variant['id']}",
                    "item_id": base_id,
                    "variant_id": variant["id"],
                    "klass": variant["klass"],
                    "text": variant["text"],
                }
            )

    seen: Dict[str, str] = {}
    for cell in cells:
        if cell["cell_id"] in seen:
            raise CorpusError(f"duplicate cell id {cell['cell_id']!r}")
        seen[cell["cell_id"]] = cell["text"]
    return sorted(cells, key=lambda c: c["cell_id"])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def apply_exclusions(cells: List[Dict[str, Any]], config: Dict[str, Any]):
    """Drop whole perturbation classes, but never silently.

    A class can be invalid for one ENGINE while remaining valid for the study --
    N2's rename is meaningless against FinMem, which states the ticker in the
    prompt independently of the news, so an N2 prompt contradicts itself rather
    than paraphrasing. That is a fact about the agent, not about the fixtures,
    which is why it is config here rather than a deletion from variants.json:
    the same frozen fixtures must serve the sibling engines unchanged.

    A dropped class MUST carry its reason. §8 forbids silent caps for a good
    reason -- three classes reported where the design called for four reads as a
    completed study, not a narrowed one.
    """
    excluded = list(config.get("excluded_klasses", []))
    reasons = config.get("exclusion_reasons", {})
    if not excluded:
        return cells, {}

    unexplained = [k for k in excluded if not str(reasons.get(k, "")).strip()]
    if unexplained:
        raise CorpusError(
            f"excluded_klasses {unexplained} have no exclusion_reasons entry; "
            "a class that is not run has to say why"
        )

    kept: List[Dict[str, Any]] = []
    dropped: Dict[str, int] = {k: 0 for k in excluded}
    for cell in cells:
        if cell["klass"] in dropped:
            dropped[cell["klass"]] += 1
        else:
            kept.append(cell)
    return kept, dropped


def parse_price_series(config: Dict[str, Any]) -> Dict[date, float]:
    """Prices as {date: close}, from the config's own list.

    Real closes are supplied with the fixture spec. `synthetic` exists for the
    rehearsal only and is recorded in the manifest, so a run against made-up
    prices can never be mistaken later for a run against real ones.
    """
    series: Dict[date, float] = {}
    for entry in config["prices"]:
        day = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        series[day] = float(entry["close"])
    if not series:
        raise CorpusError("config has no prices")
    return series


def write_pickle(path: Path, corpus: Dict[date, Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        # Protocol pinned so a corpus built today is byte-identical to one built
        # on any other 3.10; the default protocol moves between Python versions.
        pickle.dump(corpus, handle, protocol=5)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fixtures", type=Path, default=Path("data/fixtures"))
    parser.add_argument("--config", type=Path, default=Path("harness/corpus_config.json"))
    parser.add_argument("--out", type=Path, default=Path("data/corpus"))
    args = parser.parse_args(argv)

    try:
        config = load_json(args.config)
        symbol = config["symbol"]
        prices = parse_price_series(config)
        train_days = sorted(prices)[: config.get("train_days", MIN_TRAIN_DAYS)]
        decision_day = datetime.strptime(config["decision_date"], "%Y-%m-%d").date()
        next_day = datetime.strptime(config["next_date"], "%Y-%m-%d").date()

        for needed in (decision_day, next_day):
            if needed not in prices:
                raise CorpusError(f"no price for {needed}")
        if decision_day in train_days:
            # Otherwise the decision date's news is already in memory from the
            # training pass, and every cell retrieves a neighbour of itself.
            raise CorpusError(f"decision date {decision_day} overlaps the training window")

        # One neutral line per training date. It is deliberately dull: it ends up
        # in short memory and is retrievable at decision time (top_k=3), so it is
        # part of the frozen context every cell shares. Constant across variants,
        # therefore incapable of biasing a flip -- but it is context, not nothing,
        # and the report should say so rather than claim an empty memory.
        training_news = config.get("training_news")
        if isinstance(training_news, str):
            training_news = [training_news] * len(train_days)
        if not training_news:
            raise CorpusError("config has no 'training_news'; FinMem crashes on empty news")
        if len(training_news) < len(train_days):
            raise CorpusError(
                f"'training_news' has {len(training_news)} entries for {len(train_days)} training dates"
            )
        news_by_date = {day: [training_news[i]] for i, day in enumerate(train_days)}

        train_corpus = build_training_corpus(symbol, {d: prices[d] for d in train_days}, news_by_date)
        write_pickle(args.out / "train.pkl", train_corpus)

        cells = collect_cells(args.fixtures)
        cells, dropped = apply_exclusions(cells, config)
        manifest_cells = []
        for cell in cells:
            corpus = build_decision_corpus(
                symbol=symbol,
                text=cell["text"],
                decision_date=decision_day,
                next_date=next_day,
                decision_price=prices[decision_day],
                next_price=prices[next_day],
            )
            rel = Path("cells") / f"{cell['cell_id']}.pkl"
            write_pickle(args.out / rel, corpus)
            manifest_cells.append(
                {
                    "cell_id": cell["cell_id"],
                    "item_id": cell["item_id"],
                    "variant_id": cell["variant_id"],
                    "klass": cell["klass"],
                    "path": str(rel).replace("\\", "/"),
                    "text_sha256_16": text_digest(cell["text"]),
                }
            )

        manifest = {
            "builder_version": BUILDER_VERSION,
            "symbol": symbol,
            "decision_date": config["decision_date"],
            "next_date": config["next_date"],
            "train_days": [d.isoformat() for d in train_days],
            "price_source": config.get("price_source", "UNDECLARED"),
            "train_pickle": "train.pkl",
            # Recorded so the scoring report can state what was NOT run. A class
            # missing from the log and a class that produced no flips look
            # identical downstream unless the corpus says which happened.
            "excluded_klasses": {
                klass: {
                    "reason": config.get("exclusion_reasons", {})[klass],
                    "cells_dropped": count,
                }
                for klass, count in sorted(dropped.items())
            },
            "cells": manifest_cells,
        }
        # Remove cell pickles the current manifest does not name. Rebuilding after
        # excluding a class would otherwise leave its pickles lying beside the live
        # ones -- harmless while every reader goes through the manifest, and a trap
        # the moment something globs the directory instead.
        removed = []
        cells_dir = args.out / "cells"
        if cells_dir.is_dir():
            live = {entry["path"] for entry in manifest_cells}
            for stale in sorted(cells_dir.glob("*.pkl")):
                if f"cells/{stale.name}" not in live:
                    stale.unlink()
                    removed.append(stale.name)

        manifest_path = args.out / "manifest.json"
        with manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")

    except CorpusError as exc:
        print(f"corpus build failed: {exc}", file=sys.stderr)
        return 1

    print(f"train.pkl: {len(train_corpus)} dates")
    print(f"cells:     {len(manifest_cells)}")
    for klass, count in sorted(dropped.items()):
        print(f"  DROPPED {klass}: {count} cells not built - {config['exclusion_reasons'][klass]}")
    for name in removed:
        print(f"  swept stale cell: {name}")
    print(f"manifest:  {manifest_path}")
    if manifest["price_source"] == "UNDECLARED":
        print("WARNING: config declares no price_source; say whether these closes are real.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
