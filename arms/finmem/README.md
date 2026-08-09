# FinPerturb — the FinMem arm

Does a published LLM trading agent change its decision when the news is reworded
without changing its meaning? This arm is the harness that finds out for FinMem
([arXiv 2311.13743](https://arxiv.org/abs/2311.13743), pinned at `be814aa`). See
the build guide for what is being measured and why the pedantic parts are the
experiment; this file only covers **how to run the box**.

**One arm per agent under test** — see the repo-root README for the monorepo
layout. Each arm keeps its own image, compose project and dependency world,
because the thing that cannot be shared is the dependency set: FinMem pins
Python 3.10 and a 2024-era stack, and each sibling pins something else. The
scoring code is the opposite — one copy at the repo root's `scoring/`, reading
plain JSON rows that know nothing about which agent produced them.

The per-arm split also has an experimental reason. Whether a perturbation class
is even *valid* turns out to depend on the engine — see Perturbation classes
below.

## Container, not a hand-built box

The build guide's §2 assumes a hand-installed Ubuntu under WSL. This project runs
in Docker instead. The mapping:

| Guide | Here |
|---|---|
| §2.1 WSL2 + Ubuntu | Docker Desktop's own Linux VM |
| §2.2 apt tooling | `Dockerfile` — reproducible, rebuilt on demand |
| §2.2 Python 3.12 | **3.10** — FinMem pins `>=3.10,<3.11`; see the Dockerfile header |
| §2.3 keep files off `/mnt/c` | irrelevant at this I/O volume — with one exception, below |
| §2.4 keys in `~/.finperturb.env` | `.env`, read at run time, never in an image layer |
| §2.5 skeleton | the monorepo, bind-mounted at `/work`; compose starts you in this arm |

Three things this buys that the guide's approach does not: §3's dependency pain
is captured once instead of living in one person's shell history, the image is a
lockfile for everything below Python, and a key cannot leak into a layer because
none is ever passed to `docker build`.

One thing it deliberately does **not** buy: determinism of the agent. The image
pins dependencies; the model still samples at its default decoding settings, and
that variance is the thing being measured (§8.3).

## First run

```bash
cp .env.example .env      # then put the real keys in it
docker compose build
docker compose up -d
docker compose exec fp bash
```

The entrypoint refuses to start if either key is missing or still `REPLACE_ME` —
better than discovering it at call 400 of an evening-long run. For a shell
without keys, `docker compose run --rm -e FP_REQUIRE_KEYS=0 fp bash`.

## Layout

```
agents/        cloned agent repos (gitignored; their lockfiles are not)
data/
  fixtures/    frozen base items + variants — committed, and frozen means frozen
  runs/        append-only run logs — NOT committed, back up by hand
harness/       wrapper, fixture generation, runners
logs/          operational logs
```

## Scoring — the repo's, not this arm's

`scoring/` lives at the **monorepo root**, one copy for every arm — the three
pre-registered rules, the permutation null and its seed discipline; see its own
README. Every report prints the repo SHA it ran at in its *Scoring rules in
force* table, so "both arms were scored under the same rules" is checked by
reading two lines, not assumed. Nothing under `scoring/` is edited as a side
effect of arm work: a rule change is a new registration, made deliberately, and
the provenance row flags an edited `scoring/` as dirty.

The container image carries `git config --system safe.directory '*'` so the SHA
resolves from inside Docker; without it the report says
`unknown (not a git checkout)` against a bind mount git refuses to read.

Scoring runs from the repo root, against this arm's logs:

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v C:\Users\brett\finperturb:/work -w /work finperturb-finmem:dev python -m pytest scoring/test_scoring_rules.py -q
```

```bash
docker run --rm -e FP_REQUIRE_KEYS=0 -v C:\Users\brett\finperturb:/work -w /work finperturb-finmem:dev python scoring/score_pilot.py --log arms/finmem/data/runs/<run>.jsonl --out arms/finmem/data/runs/<report>.md
```

## Venvs

The harness venv is baked into the image at `/opt/harness-venv` and is on `PATH`;
rebuilding the image rebuilds it. Agent venvs go under `/opt/venvs/<agent>`, which
is a **named volume** — they survive an image rebuild, because §3 budgets one to
two days of dependency work per agent and losing that to a `docker compose build`
would be its own small tragedy.

FinMem ships a `poetry.lock`, so its venv is built from that rather than from
`.devcontainer/requirements.txt` — the lock is the pinned artifact and the
requirements file can drift from it. `POETRY_VIRTUALENVS_PATH` is already set to
the named volume, so this lands outside the bind mount:

```bash
# inside the container, per §3.2
cd agents/finmem && poetry install
poetry env info --path                          # where it landed, under /opt/venvs
poetry run pip freeze > ../finmem-lock.txt      # committed
```

## The one place the bind mount matters

Project code, fixtures and the run log live on the host and are mounted at
`/work` — right for all three, since you edit them in VS Code and the log must
outlive the container.

The exception is the agent's own mutable state. §5.2.3 snapshots and restores
FinMem's memory store, checkpoints and vector index on **every** `decide()` call
— roughly 1,100 directory copies across a run matrix. That belongs on a
container-side path or a named volume, never on the Windows bind mount, where
each copy pays the VM's filesystem tax. It is also the one directory that is
genuinely disposable: it is rebuilt from the frozen context every call.

## Perturbation classes

| Class | Status here | Note |
|---|---|---|
| N1 paraphrase | **run** | |
| N2 rename | **DROPPED for FinMem** | project lead, 2026-08-08 — see below |
| N3 no-op append | **run** | |

**Why N2 is dropped, and it is a property of the engine rather than of the
fixtures.** §4.2 replaces the company name "everywhere" — but only in the news
text, because that is all a fixture file contains. FinMem injects the ticker into
the prompt *separately*, from its own config:
`"The ticker of the stock to be analyzed is {symbol} and the current date is
{cur_date}"` ([prompts.py:16](agents/finmem/puppy/prompts.py:16)). So an N2
variant produces a prompt that names TSLA in its header and "Company A" in its
body.

That is not a meaning-preserving rewrite. It is a self-contradictory prompt, and
a decision change under it would measure the contradiction rather than
sensitivity to surface form. Worse, **§4.3's audit cannot catch it**: the
reviewer compares two texts side by side, and the contradiction is introduced
downstream by the agent's own prompt assembly.

Three options were on the table — accept and document, rename the symbol in
config per run (it namespaces memory and the portfolio, so not free), or drop.
The lead chose **drop and notate**, on the reasoning that the other two engines
must be read first: whether N2 is recoverable depends on whether an engine states
the ticker independently of the news, and that is exactly what the sibling repos
will establish.

Mechanically, the drop lives in `harness/corpus_config.json` as
`excluded_klasses`, and the builder **refuses to run** if a class is excluded
without a stated reason. Dropped counts are printed and recorded in the corpus
manifest, so a report can say what was not run rather than quietly showing three
classes where the design called for four. Re-enabling N2 for a sibling engine is
deleting one line of config.

## Things that are not automated, on purpose

- **Keys.** Nobody but you types them, and they go in `.env` only.
- **The nullity audit** (§4.3) is the project lead's, not the builder's.
- **Interpreting the numbers** (§7) is the project lead's, against a read-out rule
  fixed before the runs start.
