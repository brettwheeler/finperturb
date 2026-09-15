#!/usr/bin/env python3
"""Verify every source citation in the applicability matrices against the pinned clones.

Inputs are the two matrices, `docs/applicability-matrix.json` (null classes) and
`docs/applicability-matrix-material.json` (material classes). Each matrix records,
per engine, the arm directory and the upstream pin; the engine clone lives at
`<arm>/agents/<engine>` with its own `.git`.

Pin check, first and fatal: `git -C <clone> rev-parse HEAD` must start with the
recorded pin, or the run aborts naming the engine. Every cited file is then read
at the pin with `git show <pin>:<path>`, never from the working tree, so a locally
edited file cannot make a citation pass that would fail for anyone else.

Citation grammar, three accepted forms:

    path:line        one line
    path:line-line   inclusive range
    path             no line number (prompt templates, assets, globs)

A comma-separated bare range following a cited range binds to the preceding path
(`provider.py:270-284, 411-444`). Paths under `harness/` resolve against the arm
in this repository, and `docs/` or `scoring/` paths against the repository root,
both at the repository HEAD rather than the working tree. Cross-cutting text has
no engine context: its clone paths are resolved against every engine and must
match exactly one. Bare issue references (`#814`) and URLs are `external` and are
listed, not checked.

Statuses: ok / wide (range > 40 lines, not a failure) / missing_file /
line_out_of_range / external. Exit status is nonzero on any pin mismatch,
missing_file, line_out_of_range, or an ambiguous cross-cutting path.

Run from the repository root:

    python scripts/verify_citations.py [--out docs/citation-check-report.md]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MATRICES = ["docs/applicability-matrix.json", "docs/applicability-matrix-material.json"]
DEFAULT_OUT = "docs/citation-check-report.md"
WIDE_LINES = 40
FIRST_LINE_CHARS = 100

PATH_RE = re.compile(r"((?:[\w.\-*]+/)*[\w.\-*]+\.(?:py|html|json|toml|txt|md|yaml|yml|cfg))(?::(\d+(?:-\d+)?))?")
BARE_RANGE_RE = re.compile(r",\s*(\d+(?:-\d+)?)")
EXTERNAL_RE = re.compile(r"(?<![\w/])#\d+\b|https?://\S+")
REPO_LOCAL_PREFIXES = ("docs/", "scoring/")


class PinMismatch(RuntimeError):
    pass


@dataclass
class Row:
    matrix: str
    engine: str
    klass: str
    verdict: str
    citation: str
    status: str
    first_line: str = ""
    resolved: str = ""


@dataclass
class Repo:
    """One git repository read at one revision."""
    path: str
    rev: str
    files: set[str] = field(default_factory=set)
    _cache: dict[str, list[str]] = field(default_factory=dict)

    def load(self) -> None:
        out = subprocess.check_output(["git", "-C", self.path, "ls-tree", "-r", "--name-only", self.rev], text=True)
        self.files = set(out.splitlines())

    def match(self, pattern: str) -> list[str]:
        if pattern in self.files:
            return [pattern]
        if any(ch in pattern for ch in "*?["):
            return sorted(f for f in self.files if fnmatch.fnmatchcase(f, pattern))
        return []

    def lines(self, path: str) -> list[str]:
        if path not in self._cache:
            raw = subprocess.check_output(["git", "-C", self.path, "show", f"{self.rev}:{path}"])
            self._cache[path] = raw.decode("utf-8", errors="replace").splitlines()
        return self._cache[path]


def git(path: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", path, *args], text=True).strip()


def extract(text: str):
    """Yield (path, range_or_None) for every citation token in a string."""
    for m in PATH_RE.finditer(text):
        path, rng = m.group(1), m.group(2)
        yield path, rng
        if rng:
            tail = text[m.end():]
            while True:
                b = BARE_RANGE_RE.match(tail)
                if not b:
                    break
                yield path, b.group(1)
                tail = tail[b.end():]


def walk(matrix: dict):
    """Yield (engine, klass, verdict, text) for every string in the matrix.

    engine is an engine key or None for cross-cutting text; klass is the class
    key under engines/<engine>/classes, the cross_cutting key, or "-".
    """
    def rec(obj, engine, klass, verdict):
        if isinstance(obj, dict):
            for k, v in obj.items():
                rec(v, engine, klass, verdict)
        elif isinstance(obj, list):
            for v in obj:
                rec(v, engine, klass, verdict)
        elif isinstance(obj, str):
            yield_list.append((engine, klass, verdict, obj))

    yield_list: list = []
    for eng, e in matrix.get("engines", {}).items():
        for k, v in e.items():
            if k == "classes":
                for cls, cell in v.items():
                    rec(cell, eng, cls, str(cell.get("verdict", "-")) if isinstance(cell, dict) else "-")
            else:
                rec(v, eng, "-", "-")
    cc = matrix.get("cross_cutting", {})
    if isinstance(cc, dict):
        for k, v in cc.items():
            rec(v, None, k, "-")
    else:
        rec(cc, None, "cross_cutting", "-")
    return yield_list


def verify(matrices: list[str], root: str = ROOT, wide_lines: int = WIDE_LINES):
    """Return (rows, header_info, fatal). Raises PinMismatch before reading anything."""
    repo_head = git(root, "rev-parse", "HEAD")
    repo_at_head = Repo(root, repo_head)
    repo_at_head.load()

    # The matrices themselves are read at HEAD too, and hashed as committed bytes,
    # so the digests in the header match what any clone of this SHA checks out.
    loaded = []
    digests = []
    for mpath in matrices:
        if mpath not in repo_at_head.files:
            raise FileNotFoundError(f"{mpath} is not committed at {repo_head[:7]}; commit it before verifying")
        raw = subprocess.check_output(["git", "-C", root, "show", f"{repo_head}:{mpath}"])
        loaded.append((mpath, json.loads(raw.decode("utf-8"))))
        digests.append((mpath, hashlib.sha256(raw).hexdigest()))

    # Pin check across every engine in every matrix, before any citation is read.
    clones: dict[str, Repo] = {}
    pin_lines: list[str] = []
    for mpath, m in loaded:
        for eng, e in m["engines"].items():
            clone = os.path.join(root, e["arm"], "agents", eng)
            head = git(clone, "rev-parse", "HEAD")
            if not head.startswith(e["pin"]):
                raise PinMismatch(f"{eng}: {mpath} records pin {e['pin']} but the clone at {e['arm']}/agents/{eng} is at {head}")
            dirty = git(clone, "status", "--porcelain")
            note = "clean" if not dirty else f"working tree has {len(dirty.splitlines())} untracked/modified path(s); not read"
            pin_lines.append(f"| {eng} | `{e['pin']}` | `{head}` | {os.path.basename(mpath)} | {note} |")
            if eng not in clones:
                r = Repo(clone, head)
                r.load()
                clones[eng] = r
    arms = {eng: m["engines"][eng]["arm"] for _, m in loaded for eng in m["engines"]}

    def resolve(engine, path):
        """Return list of (repo, resolved_path, label). Empty if nothing matched."""
        if path.startswith(REPO_LOCAL_PREFIXES):
            return [(repo_at_head, p, p) for p in repo_at_head.match(path)]
        engines = [engine] if engine else list(clones)
        found = []
        for eng in engines:
            if path.startswith("harness/"):
                full = f"{arms[eng]}/{path}"
                found.extend((repo_at_head, p, p) for p in repo_at_head.match(full))
            else:
                found.extend((clones[eng], p, f"{arms[eng]}/agents/{eng}/{p}@{clones[eng].rev[:7]}") for p in clones[eng].match(path))
        return found

    rows: list[Row] = []
    fatal = 0
    for mpath, m in loaded:
        seen: set = set()
        for engine, klass, verdict, text in walk(m):
            eng_label = engine or "cross-cutting"
            for ext in EXTERNAL_RE.findall(text):
                key = (engine, klass, "ext", ext)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(Row(mpath, eng_label, klass, verdict, ext, "external"))
            for path, rng in extract(text):
                key = (engine, klass, path, rng)
                if key in seen:
                    continue
                seen.add(key)
                cite = f"{path}:{rng}" if rng else path
                cands = resolve(engine, path)
                if not cands:
                    rows.append(Row(mpath, eng_label, klass, verdict, cite, "missing_file"))
                    fatal += 1
                    continue
                if engine is None and len({id(r) for r, _, _ in cands}) > 1:
                    rows.append(Row(mpath, eng_label, klass, verdict, cite, "ambiguous",
                                    resolved="; ".join(lbl for _, _, lbl in cands)))
                    fatal += 1
                    continue
                for repo, rpath, label in cands:
                    if not rng:
                        rows.append(Row(mpath, eng_label, klass, verdict, cite, "ok", resolved=label))
                        continue
                    lines = repo.lines(rpath)
                    a, _, b = rng.partition("-")
                    lo, hi = int(a), int(b or a)
                    if lo < 1 or hi > len(lines) or lo > hi:
                        rows.append(Row(mpath, eng_label, klass, verdict, cite, "line_out_of_range",
                                        first_line=f"file has {len(lines)} lines", resolved=label))
                        fatal += 1
                        continue
                    status = "wide" if (hi - lo + 1) > wide_lines else "ok"
                    first = lines[lo - 1].strip()
                    if len(first) > FIRST_LINE_CHARS:
                        first = first[:FIRST_LINE_CHARS - 1] + "…"
                    rows.append(Row(mpath, eng_label, klass, verdict, cite, status, first_line=first, resolved=label))

    header = {
        "repo_sha": repo_head,
        "run_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "matrices": digests,
        "pin_lines": pin_lines,
    }
    return rows, header, fatal


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("`", "'")


def render(rows: list[Row], header: dict, fatal: int) -> str:
    out: list[str] = []
    out.append("# Citation check report")
    out.append("")
    out.append(f"- Repository SHA: `{header['repo_sha']}`")
    out.append(f"- Run (UTC): {header['run_utc']}")
    for mpath, digest in header["matrices"]:
        out.append(f"- SHA-256 `{mpath}` (committed bytes at that SHA): `{digest}`")
    out.append("")
    out.append("Every cited file is read at the recorded pin with `git show <pin>:<path>`; the working tree is never read.")
    out.append("")
    out.append("## Pins")
    out.append("")
    out.append("| engine | recorded pin | clone HEAD | matrix | working tree |")
    out.append("|---|---|---|---|---|")
    out.extend(header["pin_lines"])
    out.append("")
    for mpath in dict.fromkeys(r.matrix for r in rows):
        out.append(f"## {mpath}")
        out.append("")
        out.append("| engine | class | verdict | citation | status | first cited line |")
        out.append("|---|---|---|---|---|---|")
        for r in rows:
            if r.matrix != mpath or r.status == "external":
                continue
            out.append(f"| {r.engine} | {_cell(r.klass)} | {_cell(r.verdict)} | `{_cell(r.citation)}` | {r.status} | {_cell(r.first_line)} |")
        out.append("")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r.status] = counts.get(r.status, 0) + 1
    order = ["ok", "wide", "missing_file", "line_out_of_range", "ambiguous", "external"]
    summary = ", ".join(f"{k} {counts.get(k, 0)}" for k in order if k in counts)
    out.append(f"**Summary:** {len(rows)} citations — {summary}. Result: {'FAIL' if fatal else 'PASS'}.")
    out.append("")
    ext = [r for r in rows if r.status == "external"]
    out.append("## External references (not verifiable by this script)")
    out.append("")
    if ext:
        out.append("| matrix | engine | class | reference |")
        out.append("|---|---|---|---|")
        for r in ext:
            out.append(f"| {r.matrix} | {r.engine} | {_cell(r.klass)} | {_cell(r.citation)} |")
    else:
        out.append("None.")
    out.append("")
    return "\n".join(out)


def main(argv=None, root: str | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT, help="report path, relative to the repo root")
    ap.add_argument("--matrix", action="append", help="matrix path(s); default both applicability matrices")
    args = ap.parse_args(argv)
    root = root or ROOT
    matrices = args.matrix or DEFAULT_MATRICES
    try:
        rows, header, fatal = verify(matrices, root=root)
    except PinMismatch as e:
        print(f"PIN MISMATCH — aborting: {e}", file=sys.stderr)
        return 2
    report = render(rows, header, fatal)
    out_path = os.path.join(root, args.out)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report)
    summary = next(l for l in report.splitlines() if l.startswith("**Summary:**"))
    print(report if fatal else summary)
    print(f"report written to {args.out}")
    return 1 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
