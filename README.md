# FinPerturb

Does a published LLM trading agent change its buy/sell/hold decision when the
news is reworded **without changing its meaning**? Paraphrased (N1), renamed
(N2), or given an appended irrelevant sentence (N3). The agent is stochastic by
design, so the study first measures how often it disagrees with itself on
identical input (the decoding floor, φ) and reports every effect net of that.

## Layout

```
scoring/          the pre-registered scoring rules — ONE copy, every arm
arms/
  finmem/         FinMem        (arXiv 2311.13743) — the working arm
  tradingagents/  TradingAgents (arXiv 2412.20138) — cloned + pinned, no harness yet
  finagent/       FinAgent      (arXiv 2402.18485) — cloned + pinned, no harness yet
docs/             session handoffs and study notes
```

**One repo, one arm per engine** (converted from repo-per-arm on 2026-08-09).
Each arm is self-contained below its own directory — its Dockerfile, image,
compose project, named venv volume, `data/runs/` and `.env` — because the thing
that genuinely cannot be shared is the dependency set: FinMem pins Python
`>=3.10,<3.11` and a 2024-era stack, and each sibling pins something else. What
IS shared is `scoring/`, and sharing it as one directory in one tree is the
point of the monorepo: the pre-registered rules cannot drift between arms
because there is exactly one copy, and "both engines were scored under the same
rules" is answered by the repo SHA each report prints in its *Scoring rules in
force* table.

There is deliberately **no shared harness and no engine switch**. Whether a
perturbation class is even *valid* is per-engine (N2 died for FinMem because
`puppy/prompts.py:16` states the ticker independently of the news), so each
arm's harness names its engine in its own code, and a log row's provenance is
never an environment variable.

## Running

Scoring runs from the repo root, against any arm's logs (`$(pwd)` is the
repo root in WSL or a Linux/macOS shell; in Git Bash use `$(pwd -W)`, since
MSYS path conversion mangles the volume spec; in PowerShell `${PWD}`):

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v "$(pwd):/work" -w /work finperturb-finmem:dev python scoring/score_pilot.py --log arms/finmem/data/runs/<run>.jsonl --out arms/finmem/data/runs/<report>.md
```

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v "$(pwd):/work" -w /work finperturb-finmem:dev python -m pytest scoring/test_scoring_rules.py -q
```

Agent and harness work happens inside the arm — see each arm's own README.
`docker compose` from an arm's directory mounts this whole repo at `/work` and
starts you in the arm.

## Upstream engine clones

Each arm vendors its engine under `arms/<arm>/agents/<engine>` as an ordinary
clone, **gitignored but pinned**: the clone's own `.git` records the pin, the
arm's README states it, and the engine is never modified — perturbations enter
through each arm's harness, upstream code stays as published.

## AI provenance

Most of the code and prose in this repo — the scoring rules, the harnesses,
the docs, this README — was written by Claude (Anthropic, Opus- and
Fable-class models)
under the author's direction, and every commit after the initial scaffold
carries a `Co-Authored-By` trailer saying so. Stated plainly rather than left
to be inferred from trailers: candidate methods typically originated with the
model, and so did the exhaustiveness — the audits, the test suite, the
evidence discipline are the model working angles the author directed but did
not work alone. The author's role was direction and ratification — set the question,
require the rationale for each proposed method, check it against independent
reading, adopt or reject it on that basis, and make every registration
decision. The claim on record is understanding and accountability, not
unaided capability. The full disclosure as it appears in the manuscript is
[docs/ai-disclosure.md](docs/ai-disclosure.md).

What the study asks a reviewer to trust is accordingly not authorship but
mechanism: the scoring rules froze at tag `rules-registered-2026-08-09`
before any confirmatory run, the test suite pins their behavior, and every
report prints the repo SHA it was scored under. Who typed the rules matters
less than the fact that they cannot silently change.

**Roles, and the commit identity.** The documents and code speak of a *project
lead*, an *analyst* (a project role, not the analyst agents inside
TradingAgents) and an *implementer*, and the commits through the Registration
1 filing state are authored as *Dev team*. The study was scoped with a
corporate sponsor that was to supply the analyst and implementation roles; the
sponsor withdrew before any confirmatory work, which is also the gap in commit
activity between the registration snapshot and the September work. The lead
was always the author, who is now the only person on the project: every
decision the record attributes to the lead is the author's, the rehearsal
fixtures described as analyst-written are the author's own hand-written ones,
the one work order addressed to an implementer
(`docs/handoff-item2-scoring-rules.md`) went to a Claude session as the
provenance paragraph above records, and the *Dev team* identity comes from the
Quantinero organization account the repository lived under before it moved to
the author's personal account, a separate matter from the sponsor. It is kept
rather than rewritten, because history is not edited here and rewriting it
would change the commit IDs the filed registration cites. From the commit that
records the OSF filing onward, commits are authored as Brett Wheeler, at the
same address. The role vocabulary stays where it appears in the frozen
registration attachments, whose bytes cannot change.

**Section references.** Citations of the form `§n.n` in the arm READMEs, the
FinMem Dockerfile and compose file, the harness docstrings and the fixture
notes refer to the project's internal build guide — the working
specification the harness was built against — and the *gaps list* named in
the arm READMEs and the session handoff is that document's open-items list.
Neither is published. Documents that cite their own sections (the read-out
rule, the registration text) say so, or are self-evidently internal. The
references are kept because they record which requirement each piece of code
implements; nothing a reviewer needs to check depends on resolving them,
since every registered rule is stated in full in `scoring/README.md`,
`docs/readout-rule.md` and the registration text.

**Status.** The confirmatory design is registered and frozen: OSF
Registration 1, <https://doi.org/10.17605/OSF.IO/ARFT9>, filed 2026-09-17
(repository copy: `docs/osf-registration-1-analysis-plan.md`). The repository
at the filed state is archived on Zenodo under a concept DOI that resolves to
the latest release; each release carries its own version DOI — see
`CITATION.cff`. Confirmatory runs are not scheduled: the channel-applicability
audit that this repository reports is a precondition on running the suite,
and establishing it was prior to spending against it. The harness, the
frozen scoring rules, the read-out rule and the protocol are released for
any team that wishes to execute the design; Registration 2 (fixture freeze
and run matrix) is filed by whoever runs it, in their own account.

**Licence.** Code is Apache-2.0. Documentation under `docs/`, and the
registration attachments, are released under CC-BY 4.0.
