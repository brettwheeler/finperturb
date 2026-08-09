#!/usr/bin/env bash
# Preflight, then hand off. Two jobs, both about failing early.
#
# §6.2's run matrix is ~1,100 sequential calls -- an evening of wall clock. A key
# that is missing or wrong should stop the container in the first second, not at
# call 400. Nothing here ever echoes a key VALUE; only whether one is set.
set -euo pipefail

fail=0

check_key() {
    local name="$1"
    local value="${!name-}"
    if [ -z "$value" ] || [ "$value" = "REPLACE_ME" ]; then
        echo "  $name: MISSING (unset or still the placeholder)" >&2
        fail=1
    else
        echo "  $name: set (${#value} chars)"
    fi
}

echo "finperturb container"
echo "  python:  $(python --version 2>&1)"
echo "  harness: ${HARNESS_VENV:-unset}"
check_key BACKBONE_API_KEY
check_key PARAPHRASE_API_KEY

# §2.4 and §4.2: the paraphraser must not be the model under test. Identical keys
# mean one provider doing both jobs, which quietly destroys the N1 class -- the
# rewrites inherit the backbone's own phrasing and stop being an independent
# perturbation. Cheap to check here, invisible in the results if missed.
if [ -n "${BACKBONE_API_KEY-}" ] && [ "${BACKBONE_API_KEY-}" = "${PARAPHRASE_API_KEY-}" ]; then
    echo "  WARNING: both keys are identical -- the paraphraser must be a" >&2
    echo "           DIFFERENT provider from the backbone under test (§2.4)." >&2
fi

# Model identity is provenance, and §6.3 acts on it: a version change mid-run
# means discarding and rerunning every affected row. Report both models in the
# banner so every container start records what it was about to run.
echo "  backbone model:   ${BACKBONE_MODEL:-unset}"
echo "  paraphrase model: ${PARAPHRASE_MODEL:-unset}"

# FinMem's puppy/chat.py chooses its response parser with
# self.model.startswith("gpt") -- and raises NotImplementedError for anything it
# does not recognise, from inside the call, after the request has been paid for.
case "${BACKBONE_MODEL-}" in
    ""|gpt*|gemini-pro*|tgi*) ;;
    *)
        echo "  WARNING: BACKBONE_MODEL does not start with gpt/gemini-pro/tgi;" >&2
        echo "           FinMem's parse_response will raise NotImplementedError." >&2
        ;;
esac

# A floating alias silently re-points when the provider updates it, which splits
# a run across two model versions and costs every row from the older one.
case "${BACKBONE_MODEL-}" in
    ""|*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
    *)
        echo "  NOTE: BACKBONE_MODEL looks like a floating alias rather than a" >&2
        echo "        dated snapshot -- see §6.3 before running the matrix." >&2
        ;;
esac

if [ "$fail" -ne 0 ]; then
    if [ "${FP_REQUIRE_KEYS:-1}" = "1" ]; then
        echo >&2
        echo "FATAL: copy .env.example to .env and fill in the real values." >&2
        echo "       To open a shell anyway, pass -e FP_REQUIRE_KEYS=0." >&2
        exit 78   # EX_CONFIG
    fi
    echo "  (FP_REQUIRE_KEYS=0 -- continuing without keys; API calls will fail)" >&2
fi

# FinMem reads OPENAI_API_KEY from the environment, in two places that matter:
# puppy/chat.py (the decision call) and puppy/embedding.py (text-embedding-ada-002,
# which drives memory retrieval and is therefore part of the chain under test).
# The harness calls that same credential BACKBONE_API_KEY, because from our side it
# is "the model under test" rather than "OpenAI". Bridging the two names here keeps
# the key in exactly one place -- .env -- so no file inside the agent repo ever has
# to hold it, and the agent repo stays unmodified.
#
# Safe against the placeholder .env the repo ships: run.py calls bare load_dotenv(),
# whose default is override=False, so a real environment variable beats the file's
# "Enter your OpenAI API Key here".
if [ -n "${BACKBONE_API_KEY-}" ] && [ "${BACKBONE_API_KEY-}" != "REPLACE_ME" ]; then
    if [ -n "${OPENAI_API_KEY-}" ] && [ "${OPENAI_API_KEY-}" != "${BACKBONE_API_KEY-}" ]; then
        # Never silently choose between two different keys. Which model answered is
        # provenance, and §6.3 already treats a change of model identity as grounds
        # for discarding rows.
        echo "  WARNING: OPENAI_API_KEY was set and differs from BACKBONE_API_KEY;" >&2
        echo "           BACKBONE_API_KEY wins (it is the declared single source)." >&2
    fi
    export OPENAI_API_KEY="$BACKBONE_API_KEY"
    echo "  OPENAI_API_KEY: bridged from BACKBONE_API_KEY (for FinMem)"
fi

# The run log is append-only (§8.4) and lives on the bind mount, so it survives
# the container. Create the directories rather than making every writer do it.
# WORKDIR-RELATIVE, GATED ON BEING IN AN ARM: since the monorepo, /work is the
# repo root and compose starts each arm's container in its own directory. This
# script is baked into the image at /usr/local/bin, so its own path says
# nothing; the workdir says everything. The harness/ test keeps a one-off
# `docker run -w /work` (how scoring is invoked) from growing a data/ at the
# repo root that no arm reads.
if [ -d harness ]; then
    mkdir -p data/runs logs
fi

exec "$@"
