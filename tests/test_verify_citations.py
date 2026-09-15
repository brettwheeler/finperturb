"""Tests for scripts/verify_citations.py against a throwaway fixture layout.

The fixture mirrors the repository shape the script expects: a root git repo
holding the matrix and an arm harness file, and an engine clone at
<arm>/agents/<engine> with its own .git and a recorded pin.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import verify_citations as vc  # noqa: E402

ENGINE = "toyengine"
CLONE_FILE_LINES = ["line one", "line two", "line three", "line four", "line five"]


def _git(path, *args):
    subprocess.check_call(["git", "-C", path, *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _init(path):
    os.makedirs(path, exist_ok=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "t@example.com")
    _git(path, "config", "user.name", "t")


def _commit_all(path, msg="c"):
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", msg)
    return subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


@pytest.fixture
def fixture_repo(tmp_path):
    root = str(tmp_path / "root")
    arm = f"arms/{ENGINE}"
    clone = os.path.join(root, arm, "agents", ENGINE)
    _init(root)
    _write(os.path.join(root, ".gitignore"), [f"{arm}/agents/"])
    _write(os.path.join(root, arm, "harness", "h.py"), ["harness line"])
    _init(clone)
    _write(os.path.join(clone, "pkg", "mod.py"), CLONE_FILE_LINES)
    _write(os.path.join(clone, "pkg", "big.py"), [f"big {i}" for i in range(1, 61)])
    pin = _commit_all(clone)[:7]

    def build_matrix(citations: dict[str, str], cross: dict | None = None, pin_override=None):
        m = {
            "engines": {
                ENGINE: {
                    "pin": pin_override or pin,
                    "arm": arm,
                    "classes": {k: {"verdict": "run", "reason": v, "citations": []} for k, v in citations.items()},
                }
            },
            "cross_cutting": cross or {},
        }
        _write(os.path.join(root, "docs", "m.json"), [json.dumps(m)])
        _commit_all(root, "matrix")
        return "docs/m.json"

    return root, clone, pin, build_matrix


def _statuses(rows):
    return {r.citation: r.status for r in rows}


def test_statuses(fixture_repo):
    root, clone, pin, build = fixture_repo
    mpath = build({
        "A": "see pkg/mod.py:2 and pkg/mod.py:1-3 and pkg/mod.py",
        "B": "see pkg/nope.py:1 and pkg/mod.py:4-9",
        "C": "see pkg/big.py:1-60 and harness/h.py:1; upstream issue #42",
    })
    rows, header, fatal = vc.verify([mpath], root=root)
    st = _statuses(rows)
    assert st["pkg/mod.py:2"] == "ok"
    assert st["pkg/mod.py:1-3"] == "ok"
    assert st["pkg/mod.py"] == "ok"
    assert st["pkg/nope.py:1"] == "missing_file"
    assert st["pkg/mod.py:4-9"] == "line_out_of_range"
    assert st["pkg/big.py:1-60"] == "wide"
    assert st["harness/h.py:1"] == "ok"
    assert st["#42"] == "external"
    assert fatal == 2
    first = {r.citation: r.first_line for r in rows}
    assert first["pkg/mod.py:2"] == "line two"
    assert first["harness/h.py:1"] == "harness line"


def test_pin_mismatch_aborts_before_reading(fixture_repo):
    root, clone, pin, build = fixture_repo
    mpath = build({"A": "pkg/mod.py:1"}, pin_override="0000000")
    with pytest.raises(vc.PinMismatch) as ei:
        vc.verify([mpath], root=root)
    assert ENGINE in str(ei.value)


def test_working_tree_is_not_read(fixture_repo):
    root, clone, pin, build = fixture_repo
    mpath = build({"A": "pkg/mod.py:5 and pkg/mod.py:2"})
    # Shrink the file in the working tree only; the pin still has five lines.
    _write(os.path.join(clone, "pkg", "mod.py"), ["EDITED"])
    rows, header, fatal = vc.verify([mpath], root=root)
    st = _statuses(rows)
    assert st["pkg/mod.py:5"] == "ok"
    assert fatal == 0
    assert {r.citation: r.first_line for r in rows}["pkg/mod.py:2"] == "line two"
    assert "untracked/modified" in header["pin_lines"][0]


def test_cross_cutting_resolves_against_all_engines_and_report_renders(fixture_repo):
    root, clone, pin, build = fixture_repo
    mpath = build({}, cross={"note": "the engine reads pkg/mod.py:3 here"})
    rows, header, fatal = vc.verify([mpath], root=root)
    assert fatal == 0
    assert rows[0].engine == "cross-cutting" and rows[0].klass == "note" and rows[0].status == "ok"
    report = vc.render(rows, header, fatal)
    assert "Result: PASS" in report
    assert header["repo_sha"] in report
    assert header["matrices"][0][1] in report


def test_cli_exit_codes(fixture_repo):
    root, clone, pin, build = fixture_repo
    mpath = build({"A": "pkg/mod.py:1"})
    assert vc.main(["--matrix", mpath, "--out", "report.md"], root=root) == 0
    assert os.path.exists(os.path.join(root, "report.md"))
    build({"A": "pkg/mod.py:99"})
    assert vc.main(["--matrix", mpath, "--out", "report.md"], root=root) == 1
    build({"A": "pkg/mod.py:1"}, pin_override="0000000")
    assert vc.main(["--matrix", mpath, "--out", "report.md"], root=root) == 2
