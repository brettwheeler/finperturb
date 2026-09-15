#!/usr/bin/env python3
"""EXPLORATORY. Does the agent's rationale pick up the N3 distractor sentence?

N3 appends one fluent, decision-irrelevant sentence to the base news item. The
registered scoring asks only whether the action distribution moves. This script
asks a mechanistic side question over the pilot rows: does the appended sentence
show up in the agent's stated rationale, and if it does, does the action differ
from the item's modal BASE action more often than when it does not.

This is not a registered analysis, governs nothing, and is reported as
exploratory. The pilot rows are fabricated-fixture rehearsal rows (see the
registration's Existing-data section); nothing here is a finding about the agent.

Method. For each N3 variant in the pilot fixtures, the appended clause is the
suffix of the variant text after its base text (recoverable by construction: the
fixture notes state the preceding text is byte-identical). Each clause is mapped
to a small set of discriminating terms chosen so that none occurs in the base
item, in any other item, or in the four filler training-day news items the
memory holds (checked mechanically below, and the run aborts if the check
fails). A rationale "mentions" the distractor when any term occurs. The same
detector is run over every non-N3 rationale as a false-positive control: those
runs never saw the clause, so any hit there is detector noise.

Run from the repo root:

    python scripts/analyze_n3_incorporation.py [--out docs/n3-incorporation-<date>.md]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import pickle
import re
import subprocess
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARM = os.path.join(ROOT, "arms", "finmem", "data")

# Discriminating terms per N3 variant. "careers" alone is NOT used for S07 because
# the filler training news item of 2026-06-03 says "careers page"; "website" and
# "refreshed" are the clause's own words.
TERMS = {
    "S01-N3-1": ["visitor centre", "visitor center", "lobby", "refurbish"],
    "S03-N3-1": ["visitor centre", "visitor center", "weekend", "opening hours"],
    "S04-N3-1": ["sustainability"],
    "S05-N3-1": ["car park", "parking", "repav", "fremont"],
    "S06-N3-1": ["owner's manual", "owner’s manual", "manual portal", "languages"],
    "S07-N3-1": ["careers website", "careers site", "website"],
}
# Terms that identify the four filler training-day news items held in memory
# (see corpus/<name>/train.pkl). Used only for the comparison table: the agent
# demonstrably cites low-relevance memory items, so silence on the appended
# clause is not silence on low-relevance content in general.
FILLER = {
    "investor-relations schedule (06-01)": ["investor relations", "investor-relations", "ir event"],
    "registered office filing (06-02)": ["registered office", "office address"],
    "careers page openings (06-03)": ["careers", "career page", "facilities admin"],
    "industry directory entry (06-04)": ["industry directory", "directory"],
}
DISMISSAL = re.compile(
    r"\b(irrelevant|immaterial|not material|no bearing|non-material|routine|cosmetic|"
    r"no (?:direct )?(?:impact|effect|relevance)|does not (?:affect|change|alter)|"
    r"not (?:a )?(?:catalyst|market-moving|decision-relevant)|noise)\b", re.I)


def load_fixtures():
    """Return {variant_id: (corpus, item_id, clause)}, plus every base/train text."""
    clauses, other_texts = {}, []
    for corpus in sorted(os.listdir(os.path.join(ARM, "fixtures"))):
        fdir = os.path.join(ARM, "fixtures", corpus)
        if not os.path.isdir(fdir):
            continue
        bases = {b["id"]: b["text"] for b in json.load(open(os.path.join(fdir, "base_items.json"), encoding="utf-8"))}
        other_texts.extend(bases.values())
        vpath = os.path.join(fdir, "variants.json")
        if os.path.exists(vpath):
            for v in json.load(open(vpath, encoding="utf-8")):
                if v["klass"] != "N3":
                    continue
                base = bases[v["base_id"]]
                assert v["text"].startswith(base), f"{v['id']}: preceding text is not byte-identical to base"
                clauses[v["id"]] = (corpus, v["base_id"], v["text"][len(base):].strip())
        tp = os.path.join(ARM, "corpus", corpus, "train.pkl")
        if os.path.exists(tp):
            for day in pickle.load(open(tp, "rb")).values():
                for news in day.get("news", {}).values():
                    other_texts.extend(news)
    return clauses, other_texts


def check_terms(clauses, other_texts):
    """At least one term per set must occur in its own clause (the others are
    spelling variants); no term may occur in any base or training-day text."""
    problems = []
    low_others = [t.lower() for t in other_texts]
    for vid, terms in TERMS.items():
        clause = clauses[vid][2].lower()
        if not any(t.lower() in clause for t in terms):
            problems.append(f"{vid}: no detector term occurs in its clause")
        for t in terms:
            hits = [o[:60] for o in low_others if t.lower() in o]
            if hits:
                problems.append(f"{vid}: term {t!r} occurs in base/train text: {hits}")
    return problems


def mentions(text: str, vid: str) -> list[str]:
    low = text.lower()
    return [t for t in TERMS[vid] if t.lower() in low]


def modal_base(rows):
    """{(run_id, item): modal BASE action or None if tied}."""
    out = {}
    by = defaultdict(Counter)
    for r in rows:
        if r["klass"] == "BASE" and r["status"] == "ok":
            by[(r["run_id"], r["item_id"])][r["action"]] += 1
    for k, c in by.items():
        top = c.most_common(2)
        out[k] = None if len(top) > 1 and top[0][1] == top[1][1] else top[0][0]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=f"docs/n3-incorporation-{_dt.date.today().isoformat()}.md")
    args = ap.parse_args(argv)

    clauses, other_texts = load_fixtures()
    problems = check_terms(clauses, other_texts)
    if problems:
        raise SystemExit("term check failed:\n  " + "\n  ".join(problems))

    logs = sorted(glob.glob(os.path.join(ARM, "runs", "*.jsonl")))
    rows = []
    for lg in logs:
        for line in open(lg, encoding="utf-8"):
            r = json.loads(line)
            r["_log"] = os.path.basename(lg)
            rows.append(r)
    modal = modal_base(rows)

    n3 = [r for r in rows if r["klass"] == "N3" and r["status"] == "ok"]
    ctrl = [r for r in rows if r["klass"] != "N3" and r["status"] == "ok"]

    # Per-variant tally over N3 rows.
    per = defaultdict(lambda: {"n": 0, "mention": 0, "dismiss": 0, "flip_m": [0, 0], "flip_nm": [0, 0], "tied": 0, "actions_m": Counter(), "actions_nm": Counter()})
    for r in n3:
        vid = r["variant_id"]
        p = per[(r["_log"], vid)]
        p["n"] += 1
        hit = mentions(r["rationale"] or "", vid)
        base = modal.get((r["run_id"], r["item_id"]))
        if base is None:
            p["tied"] += 1
        if hit:
            p["mention"] += 1
            if DISMISSAL.search(r["rationale"] or ""):
                p["dismiss"] += 1
            p["actions_m"][r["action"]] += 1
            if base is not None:
                p["flip_m"][1] += 1
                p["flip_m"][0] += int(r["action"] != base)
        else:
            p["actions_nm"][r["action"]] += 1
            if base is not None:
                p["flip_nm"][1] += 1
                p["flip_nm"][0] += int(r["action"] != base)

    # False-positive control: run every detector over every non-N3 rationale of the same item.
    fp = Counter()
    fp_n = Counter()
    for r in ctrl:
        for vid, (corpus, item, _) in clauses.items():
            if item != r["item_id"]:
                continue
            fp_n[vid] += 1
            if mentions(r["rationale"] or "", vid):
                fp[vid] += 1

    filler = {k: [0, 0] for k in FILLER}
    for r in rows:
        if r["status"] != "ok":
            continue
        low = (r["rationale"] or "").lower()
        for k, terms in FILLER.items():
            filler[k][1] += 1
            filler[k][0] += int(any(t in low for t in terms))

    sha = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()
    out = []
    out.append("# N3 distractor incorporation — exploratory, pilot rows only")
    out.append("")
    out.append(f"Generated {_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')} at `{sha}` by `scripts/analyze_n3_incorporation.py`.")
    out.append("")
    out.append("**Status: exploratory.** Not a registered analysis; governs nothing. The rows are the fabricated-fixture rehearsal runs disclosed in Registration 1 (§ Existing data). This asks a mechanistic side question: when N3 appends an irrelevant sentence, does the agent's rationale mention it, and does the action differ from the modal BASE action more often when it does.")
    out.append("")
    out.append(f"Rows: {len(rows)} across {len(logs)} logs; N3 rows with status ok: {len(n3)}; non-N3 control rows: {len(ctrl)}.")
    out.append("")
    out.append("## Clauses and detectors")
    out.append("")
    out.append("| variant | corpus | item | appended clause | detector terms |")
    out.append("|---|---|---|---|---|")
    for vid, (corpus, item, clause) in sorted(clauses.items()):
        out.append(f"| {vid} | {corpus} | {item} | {clause} | {', '.join(TERMS[vid])} |")
    out.append("")
    out.append("Term check passed: no detector term occurs in any base item or in the four filler training-day news items. The S07 detector deliberately excludes the bare word *careers*, which the 2026-06-03 filler item also uses.")
    out.append("")
    out.append("## Per-variant tally")
    out.append("")
    out.append("| log | variant | n | mentions | of which dismissed | tied base | flip \\| mentioned | flip \\| not mentioned | actions \\| mentioned | actions \\| not |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    tot = Counter()
    for (lg, vid), p in sorted(per.items()):
        fm = f"{p['flip_m'][0]}/{p['flip_m'][1]}" if p["flip_m"][1] else "–"
        fnm = f"{p['flip_nm'][0]}/{p['flip_nm'][1]}" if p["flip_nm"][1] else "–"
        out.append(f"| {lg} | {vid} | {p['n']} | {p['mention']} | {p['dismiss']} | {p['tied']} | {fm} | {fnm} | {dict(p['actions_m']) or '–'} | {dict(p['actions_nm']) or '–'} |")
        tot["n"] += p["n"]; tot["mention"] += p["mention"]; tot["dismiss"] += p["dismiss"]
        tot["fm0"] += p["flip_m"][0]; tot["fm1"] += p["flip_m"][1]
        tot["fnm0"] += p["flip_nm"][0]; tot["fnm1"] += p["flip_nm"][1]
    out.append("")
    out.append("## Pooled")
    out.append("")
    out.append(f"- N3 rationales mentioning the distractor: {tot['mention']} / {tot['n']}")
    out.append(f"- Of those, rationales that also dismiss it as immaterial (regex, see script): {tot['dismiss']}")
    out.append(f"- Action differs from modal BASE, given mention: {tot['fm0']} / {tot['fm1']} (tied-baseline items excluded)")
    out.append(f"- Action differs from modal BASE, given no mention: {tot['fnm0']} / {tot['fnm1']}")
    out.append("")
    out.append("Pooling across logs and items is for legibility only; runs within an item are correlated and the registered analysis bootstraps items, not runs. No inference is drawn here.")
    out.append("")
    out.append("## False-positive control")
    out.append("")
    out.append("The same detector run over every non-N3 rationale of the same item. Those runs never saw the clause, so a hit is detector noise (or the model volunteering the topic unprompted).")
    out.append("")
    out.append("| variant | control rows | hits |")
    out.append("|---|---|---|")
    for vid in sorted(clauses):
        out.append(f"| {vid} | {fp_n[vid]} | {fp[vid]} |")
    out.append("")
    out.append("## Comparison: does the rationale cite the filler memory items?")
    out.append("")
    out.append("The memory holds four deliberately low-relevance training-day items. If the agent cites those, silence on the appended clause is a fact about the clause's position (appended to the decision-day item) rather than about low-relevance content in general.")
    out.append("")
    out.append("| filler item | rationales citing it | of rows |")
    out.append("|---|---|---|")
    for k, (h, n) in filler.items():
        out.append(f"| {k} | {h} | {n} |")
    out.append("")
    out.append("## Reading (exploratory, not a finding)")
    out.append("")
    out.append("The appended clause is never named in any of the N3 rationales, while the filler memory items that FinMem presents as separate retrieved rows are named routinely. The plausible mechanism is positional: FinMem's prompt lists each retrieved memory row as its own numbered item and asks the model to reason over the list, so a low-relevance *row* is addressed and dismissed, whereas a low-relevance *sentence inside* the decision-day row is absorbed into that row's summary. Under that reading, any N3 movement the registered analysis finds is not the model reasoning about the distractor; it is the perturbation changing the row's surface form. That is consistent with N3's registered role as a null class, and it argues for reporting N3 and N1 movement on the same footing rather than treating N3 as the weaker manipulation. To be tested, not assumed: it would take a variant that inserts the distractor as its own memory row.")
    out.append("")
    out.append("## Mentioning rationales, verbatim excerpts")
    out.append("")
    for r in n3:
        hit = mentions(r["rationale"] or "", r["variant_id"])
        if not hit:
            continue
        txt = (r["rationale"] or "").replace("\n", " ")
        i = min(txt.lower().find(t.lower()) for t in hit if txt.lower().find(t.lower()) >= 0)
        lo, hi = max(0, i - 120), min(len(txt), i + 160)
        out.append(f"- `{r['_log']}` {r['cell_id']} rep {r['rep']} → **{r['action']}** (modal BASE {modal.get((r['run_id'], r['item_id']))}): …{txt[lo:hi]}…")
    out.append("")
    path = os.path.join(ROOT, args.out)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out[out.index("## Pooled"):out.index("## False-positive control")]))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
