# FinPerturb harness image.
#
# This is the build guide's §2.2 (apt tooling) made reproducible. What it
# deliberately does NOT contain is §2.4: no key is ever baked in. Keys arrive at
# `docker run` time from the host environment, so this image is safe to rebuild,
# tag, or push without leaking anything.
#
# PYTHON 3.10, NOT THE GUIDE'S 3.12, and the subject repo is what decides it.
# FinMem's pyproject.toml pins `python = ">= 3.10, < 3.11"` and its own
# .devcontainer/Dockerfile is python:3.10.13-bookworm. Its dependency set is
# 2024-era (torch 2.2, guardrails-ai 0.3.2, langchain-community 0.0.15) and does
# not resolve on 3.12. Forcing 3.12 would mean unpinning the agent's own
# dependencies -- that is modifying the thing under test, which is the one edit
# this experiment cannot afford. The harness's own deps (httpx, tenacity, numpy,
# pytest) are all fine on 3.10, so 3.10 costs us nothing and costs FinMem
# everything to avoid.
#
# On §8.7 ("no caching in the call path, anywhere"): nothing here installs an
# HTTP proxy or a response cache. PIP_NO_CACHE_DIR affects package installs only
# and has no bearing on the agent's LLM calls -- killing those caches is done in
# the wrapper (§5.2.5), because they live inside the agent repo.

FROM python:3.10-slim-bookworm

ARG UID=1000
ARG GID=1000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VENV_ROOT=/opt/venvs \
    HARNESS_VENV=/opt/harness-venv \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PATH=/opt/harness-venv/bin:/opt/poetry/bin:$PATH

# libgomp1 is faiss-cpu's runtime dependency. FinMem's own devcontainer uses the
# full python image, which carries it; on slim it has to be asked for, and its
# absence surfaces as an ImportError deep inside the memory module rather than
# as a missing package.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        jq \
        less \
        libgomp1 \
        sqlite3 \
        unzip \
 && rm -rf /var/lib/apt/lists/*

# Run as a non-root UID matching the host's, so the fixtures and run logs
# written into the bind-mounted project are not root-owned on the host side.
RUN if ! getent group ${GID} >/dev/null 2>&1; then groupadd -g ${GID} fp; fi \
 && if ! getent passwd ${UID} >/dev/null 2>&1; then useradd -m -u ${UID} -g ${GID} -s /bin/bash fp; fi \
 && mkdir -p ${VENV_ROOT} && chown -R ${UID}:${GID} ${VENV_ROOT}

# Poetry in its own venv, so its dependency set cannot collide with the
# harness's or with FinMem's. POETRY_VIRTUALENVS_PATH points at the named
# volume, so `poetry install` inside agents/finmem lands there rather than in
# the bind-mounted repo -- Linux binaries have no business on the host filesystem.
ENV POETRY_VIRTUALENVS_PATH=/opt/venvs
RUN python -m venv ${POETRY_HOME} \
 && ${POETRY_HOME}/bin/pip install --upgrade pip \
 && ${POETRY_HOME}/bin/pip install "poetry>=1.8,<2" \
 && ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry

# The harness venv is baked into the image, so it is rebuilt with the image.
# Agent venvs are NOT: they live under ${VENV_ROOT}, which compose mounts as a
# named volume, because §3 budgets one to two days of dependency pain per agent
# repo and that must survive an image rebuild.
COPY harness/requirements.txt /tmp/harness-requirements.txt
RUN python -m venv ${HARNESS_VENV} \
 && ${HARNESS_VENV}/bin/pip install --upgrade pip setuptools wheel \
 && ${HARNESS_VENV}/bin/pip install -r /tmp/harness-requirements.txt \
 && chown -R ${UID}:${GID} ${HARNESS_VENV}

# The repo's scoring/ prints the SHA it ran at into every report's provenance
# table. Git refuses to read a repo whose owner is not the current user, and a
# Windows bind mount fails that test by construction -- so without this the
# report says "unknown (not a git checkout)" against a checkout that is plainly
# there. A blanket exception is the right scope HERE and only here: the
# container is a single-user disposable box, and this line keeps the workaround
# out of anyone's host config.
RUN git config --system --add safe.directory '*'

# sed strips CR: a checkout with CRLF endings would break the shebang, and the
# failure reads "no such file or directory" against a file that is plainly there.
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh \
 && chmod +x /usr/local/bin/entrypoint.sh

USER ${UID}:${GID}
WORKDIR /work

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
