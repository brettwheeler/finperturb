#!/usr/bin/env python3
"""One minimal call per model id: does the key accept it, and what answers?

§6.2 says measure before launching the matrix, and this is the smallest useful
measurement. It exists to settle three things that guessing gets wrong:

  ACCESS      a key scoped to an alias may or may not accept the dated snapshot.
              Cheaper to ask than to discover 40 embedding calls into a train pass.
  IDENTITY    the response carries the RESOLVED model. That is the value §6.3's
              single-version assertion should run against -- what answered, not
              what we asked for. It is also the mitigation that makes running
              against a floating alias survivable.
  COST        usage tokens and latency for one trivial call, so the matrix
              estimate rests on a measurement.

Sends the same minimal payload FinMem sends -- model and messages, nothing else
(chat.py:123) -- so the probe exercises the real request shape rather than a
tidier one of our own. No temperature, no max_tokens: §8.3's default decoding.

Never prints the key.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import httpx

ENDPOINT = "https://api.openai.com/v1/chat/completions"


def probe(model: str, api_key: str, endpoint: str) -> int:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
    }
    started = time.monotonic()
    try:
        response = httpx.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=120.0,
        )
    except httpx.HTTPError as exc:
        print(f"{model}: TRANSPORT ERROR {type(exc).__name__}: {exc}")
        return 1
    elapsed = time.monotonic() - started

    if response.status_code != 200:
        # Body can echo the key in some error shapes; print status and the API's
        # message field only, never the raw body.
        try:
            message = response.json().get("error", {}).get("message", "<no message>")
        except ValueError:
            message = "<unparseable body>"
        print(f"{model}: HTTP {response.status_code} - {message}")
        return 1

    body = response.json()
    usage = body.get("usage", {})
    resolved = body.get("model", "<absent>")
    content = body["choices"][0]["message"]["content"].strip()

    print(f"{model}: OK in {elapsed:.2f}s")
    print(f"    resolved model: {resolved}")
    print(f"    usage: prompt={usage.get('prompt_tokens')} completion={usage.get('completion_tokens')} total={usage.get('total_tokens')}")
    if "completion_tokens_details" in usage:
        # Reasoning tokens bill as output. If this is non-zero at default effort,
        # the matrix estimate changes by whatever multiple it implies.
        print(f"    completion detail: {usage['completion_tokens_details']}")
    print(f"    content: {content[:80]!r}")
    if resolved != model:
        print(f"    NOTE: asked for {model}, answered by {resolved} -- alias resolution.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="+", help="model ids to probe, in preference order")
    parser.add_argument("--endpoint", default=ENDPOINT)
    args = parser.parse_args(argv)

    api_key = os.environ.get("BACKBONE_API_KEY", "")
    if not api_key or api_key == "REPLACE_ME":
        print("BACKBONE_API_KEY is unset or still the placeholder", file=sys.stderr)
        return 2

    failures = 0
    for model in args.models:
        failures += probe(model, api_key, args.endpoint)
    return 1 if failures == len(args.models) else 0


if __name__ == "__main__":
    raise SystemExit(main())
