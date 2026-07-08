# CLAUDE.md — ONDEWO S2T Python Client

## Project Overview

This is the official Python client library for the **ONDEWO Speech-to-Text (S2T)** gRPC service.
It exposes both a synchronous (`Client`) and an asynchronous (`AsyncClient`) interface, each backed
by a generated service wrapper (`Speech2Text`) that delegates directly to the gRPC stub.

**Package name:** `ondewo-s2t-client`
**Current version:** `7.3.0`
**Python:** 3.9 – 3.12

---

## Repository Layout

```
ondewo/s2t/
  client/
    client.py                  # Sync client entry-point
    async_client.py            # Async client entry-point
    client_config.py           # ClientConfig dataclass
    services_container.py      # Holds sync service instances  (auto-generated)
    async_services_container.py# Holds async service instances (auto-generated)
    services/
      speech_to_text.py        # Sync  Speech2Text service wrapper (auto-generated)
      async_speech_to_text.py  # Async Speech2Text service wrapper (auto-generated)
  scripts/
    generate_services.py       # Code-generator: reads proto → writes service wrappers
  speech_to_text_pb2.py        # Generated protobuf message classes
  speech_to_text_pb2_grpc.py   # Generated gRPC stub classes
examples/
  file_transcription_example.py
  streaming_example.py
  ondewo-s2t-with-certificate.ipynb
  audiofiles/                  # sample_1.wav, sample_2.wav
test/
  unit/
    conftest.py                # Shared pytest fixtures
    test_sync_client.py        # Unit tests – sync client & service
    test_async_client.py       # Unit tests – async client & service
```

---

## Architecture

The library follows a thin-wrapper pattern:

```
Client / AsyncClient
  └── ServicesContainer / AsyncServicesContainer
        └── Speech2Text (sync) / Speech2Text (async)
              └── Speech2TextStub  ← gRPC stub (created per-call via stub property)
```

- **`Client`** inherits `BaseClient` from `ondewo-client-utils`.  Calls `_initialize_services()` which
  builds a `ServicesContainer` holding an instance of the sync `Speech2Text` service.
- **`AsyncClient`** mirrors `Client` but uses `AsyncBaseClient` and the async `Speech2Text` service.
- The `stub` property on each service class is **not cached** — a new `Speech2TextStub` is created on
  every RPC call.  This is intentional (ensures the channel reference stays live after reconnects).
- Service files (`services/speech_to_text.py`, `services/async_speech_to_text.py`,
  `services_container.py`, `async_services_container.py`, `client.py`, `async_client.py`) are
  **auto-generated**.  Do not edit them manually.

---

## Development Setup

### Prerequisites

- [Miniconda / Anaconda](https://docs.conda.io/en/latest/miniconda.html)
- Python 3.10 (used by the project conda env)
- `make`

### Conda environment

```bash
conda create -y --name ondewo-s2t-client-python-py310 python=3.10
conda activate ondewo-s2t-client-python-py310
pip install -r requirements-dev.txt
```

### Pre-commit hooks

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

---

## Running Tests

```bash
# All unit tests (auto-detects conda env via pytest.ini)
conda run -n ondewo-s2t-client-python-py310 pytest test/unit

# With coverage report
make test

# Only sync tests
conda run -n ondewo-s2t-client-python-py310 pytest test/unit/test_sync_client.py

# Only async tests
conda run -n ondewo-s2t-client-python-py310 pytest test/unit/test_async_client.py
```

Tests use `pytest-asyncio` (asyncio_mode = auto) and mock all gRPC infrastructure —
no running S2T server is required.

---

## Code Generation

The service wrappers are generated from the proto definitions in the `ondewo-s2t-api` submodule.

```bash
# Regenerate protobuf Python code
make generate_ondewo_protos

# Regenerate service wrapper files
make generate_services

# Regenerate async variants from sync services
make create_async_services
```

**Do not edit** the following files manually — they will be overwritten:
- `ondewo/s2t/client/client.py`
- `ondewo/s2t/client/async_client.py`
- `ondewo/s2t/client/services_container.py`
- `ondewo/s2t/client/async_services_container.py`
- `ondewo/s2t/client/services/speech_to_text.py`
- `ondewo/s2t/client/services/async_speech_to_text.py`

---

## Key Makefile Targets

| Target | Description |
|--------|-------------|
| `make test` | Run unit tests with HTML + terminal coverage report |
| `make test_unit` | Run unit tests without coverage |
| `make flake8` | Run flake8 linter |
| `make mypy` | Run mypy type checker |
| `make generate_services` | Regenerate service wrappers from protos |
| `make build` | Full build (submodules → protos → services → setup.py) |
| `make setup_developer_environment_locally` | Install pre-commit hooks + dev dependencies |

---

## Release Process

1. Update `ONDEWO_S2T_VERSION` in `Makefile`
2. Update `RELEASE.md`
3. Run `make update_setup` to bump version in `setup.py`
4. Run `make ondewo_release` (requires devops-accounts credentials)

---

## Notes for Claude

- **Service files are auto-generated** — suggest edits to `generate_services.py` instead.
- **The `stub` property is non-cached** — patch `Speech2TextStub` at the module level in tests.
- **Conda env name** is `ondewo-s2t-client-python-py310` — always use
  `conda run -n ondewo-s2t-client-python-py310` for test/lint commands.
- **asyncio_mode = auto** is set in `pytest.ini` — async test functions do not need
  `@pytest.mark.asyncio`.
- The `.gitignore` tracks `.vscode/` explicitly — vscode config files use git `force-add` or the
  gitignore exemptions at the bottom of the file.

---

## Python 3.9 Compatibility

All generated and hand-written code **must be compatible with Python 3.9**. Enforce these rules:

- **No `X | Y` union syntax** — use `Union[X, Y]` from `typing` instead.
- **No `list[...]`, `dict[...`, `tuple[...]` as generic type hints** — use `List`, `Dict`, `Tuple`
  from `typing` instead (built-in generics require Python 3.9+ only for runtime use; the `from
  __future__ import annotations` trick avoids the issue but is not required here — just use `typing`).
- **No `match`/`case` statements** — added in Python 3.10.
- **No `TypeAlias` or `ParamSpec`** without a `typing_extensions` fallback.
- **No `str.removeprefix` / `str.removesuffix`** — added in Python 3.9, so these are actually fine.
- **`asyncio.get_event_loop()`** deprecation warnings start in 3.10; prefer
  `asyncio.get_event_loop_policy().get_event_loop()` or passing loops explicitly when needed.
- Always import `annotations` generics from `typing`, not from the built-in types, to stay safe
  across the full 3.9–3.12 range.

---

## Makefile Cross-Platform Rules (macOS + Ubuntu)

The Makefile must work on both macOS (BSD tools) and Ubuntu (GNU tools). Follow these rules for any Makefile edits:

### In-place file editing

Never use `sed -i` for in-place edits — BSD sed (macOS) and GNU sed (Linux) handle `-i` differently, and `sed -i ''` breaks Make's recipe quoting when expanded via a variable.

**Always use `perl -i -pe`** — available on both platforms, no quoting issues:

```makefile
# Simple substitution
@perl -i -pe 's/foo/bar/g' file.txt

# With Make variable expansion (use double quotes so the shell expands the var)
@perl -i -pe "s/version='[0-9]+\.[0-9]+\.[0-9]+'/version='${MY_VERSION}'/g" file.txt

# Multiple substitutions, skip a line pattern
perl -i -pe 'next if /skip this line/; s/^(\s*)def /\1async def /g; s/old/new/g' "$$file"
```

### Other BSD vs GNU pitfalls

| Command | Wrong | Right |
| ------- | ----- | ----- |
| `chmod` recursive | `chmod a+rw dir -R` | `chmod -R a+rw dir` |
| `sleep` | `sleep 5s` | `sleep 5` |
| Shell exit in `if` | `echo "msg" & exit 1` | `echo "msg"; exit 1` |

## Working Principles

Behavioral guidelines to reduce common mistakes. They bias toward caution over speed; for trivial tasks, use judgment.

### Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Surgical changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that _your_ changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### Goal-driven execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and
clarifying questions come before implementation rather than after mistakes.

## Logging

```python
from loguru import logger as log
```

- **Levels:** `log.trace()`, `log.debug()`, `log.info()`, `log.warning()`, `log.error()`, `log.exception()`. Choose by
  hotness/verbosity — `trace` for per-token / hot-path detail, `debug` for routine method entry/exit, `info` for notable
  lifecycle events, `warning` / `error` / `exception` for problems.
- **Interpolate with f-strings, not loguru's `{}` positional args.** Consistent with the Code Style rule, use
  `f"…{value}"`; only add the `f` prefix when the string actually interpolates (`"START: …"` with no params stays a
  plain string).
- **`START:` / `DONE:` bracketing.** Wrap a method (or other notable operation) with a `START:` line at entry and a
  `DONE:` line at exit, both naming `ClassName: method_name` (append `: param={value}` context where useful):

  ```python
  log.debug("START: IntentBertClassifier: predict")
  ...
  log.debug(f"DONE: IntentBertClassifier: predict. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

- **Timing uses `perf_counter()`, rendered `:.5f`.** Measure elapsed time with `time.perf_counter()` captured as a start
  value and subtracted at the `DONE:` line; always format the elapsed value with the `:.5f` spec:

  ```python
  from time import perf_counter

  start_time: float = perf_counter()
  ...
  log.info(f"DONE: SESSION SERVICER: DetectIntent. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

  Never measure a duration with `time.time()` — reserve `time.time()` for wall-clock timestamps (epoch seconds persisted
  to a DB / proto, unique-id or filename stamps). `perf_counter()` has an undefined epoch and must not be stored or
  compared across processes.

## Docstrings

Google-style, triple double-quotes:

```python
"""
Short imperative summary line.

Args:
    param_name (type):
        Description of the parameter.

Returns:
    type:
        Description of the return value.

Raises:
    ExceptionType:
        When this exception is raised.
"""
```

## Git Commits

- **Never include Claude as author or co-author** in commit messages, PR descriptions, or any other text. Do not add
  `Co-Authored-By: Claude…` trailers, "Generated with Claude Code" footers, or any similar attribution.
- The user's own git author identity (already configured in git) is the only identity that should appear on commits.
- This rule overrides the default Claude Code commit-template guidance.
- **Never prepend the JIRA ticket ID** (e.g. `[OND211-2386]`) to the commit subject yourself. The `giticket` pre-commit
  hook reads the ticket from the branch name (`(feature|bugfix|support|hotfix)/<TICKET>-…`) and prepends `[<ticket>]`
  (with a trailing space) automatically. Writing the prefix manually produces a duplicate like
  `[OND211-2386] [OND211-2386] feat: …`. Write the subject as plain Conventional Commits (`feat: …`, `fix(scope): …`,
  `docs(types): …`) and let the hook add the prefix on commit.

## General Principles

- Follow existing patterns before introducing new abstractions.
- Keep changes minimal and consistent with surrounding code.
- Validate inputs early with descriptive, context-rich error messages.
- Use context managers for files, sockets, and thread pools.
- Prefer region comments for grouping methods in files that already use them.
- End edited Markdown and YAML files with a trailing newline.

## Release gotchas (hard-won this session)

These bit us during the 6.14.0 release. Keep them in mind when releasing.

- **Trust the registry, not the log.** `make release_all_clients` wraps each client in `|| echo "Already released …"`, so a *failed* release is reported as "done". After any release, verify the GitHub release **and** the published package (PyPI / npm) directly.
- **`npm install failed after 5 attempts` in a release log is usually a red herring** — that text is the echo *inside* the docker `RUN for i in 1..5; do npm install …` retry loop, not a real failure (`npm install` succeeds → `#10 DONE`). Look further down for the real error (a TTY error, an eslint failure, a `setup.py` error).
- **Codegen must run TTY-free.** The `docker run` that invokes the proto-compiler must not pass `-it` — non-interactively it fails with `cannot attach stdin to a TTY-enabled container because stdin is not a terminal`. Fix the script (drop `-it`), or run the whole release under a pseudo-TTY: `script -qc 'make …' /dev/null`.
- **Release Makefiles print secrets.** Some `docker run … -e <TOKEN>=…` recipe lines lack a leading `@`, so `make` echoes the expanded token. Rotate any token printed during a release; fix by prefixing the recipe line with `@`.
- The release auto-pulls the **latest** `ondewo-proto-compiler` tag.
- **npm package names are inconsistent** — e.g. the JS client publishes as `@ondewo/ondewo-nlu-client-js` (double `ondewo`), not `@ondewo/nlu-client-js`. Check `src/package.json`'s `name` before querying npm.
- **PyPI build needs setuptools.** The release image (`Dockerfile.utils`) is `python:3.12-slim`, which bundles no `setuptools`, so `python setup.py sdist bdist_wheel` dies with `ModuleNotFoundError: No module named 'setuptools'`. `Dockerfile.utils` must `pip install … setuptools wheel`.

## Python tooling — uv + ruff + mypy + pyproject.toml (this session's refactor)

This repo was migrated off `setup.py` / `.flake8` / `mypy.ini` to a single **pyproject.toml** with **uv**, **ruff**, and **mypy**. Going forward:

- **Build backend stays setuptools** (for PyPI compatibility). Build with `python -m build --no-isolation` or `uv build` — NOT `python setup.py sdist bdist_wheel` (setup.py is deleted). `Dockerfile.utils` installs `twine setuptools wheel build`.
- **Dependencies via uv + a committed `uv.lock`.** CI runs `uv sync --extra dev --frozen`. To add/change a dep: edit `[project.dependencies]`/`[project.optional-dependencies].dev` in pyproject.toml then `uv lock`.
- **Lint is ruff** (`[tool.ruff]`, line-length 120, generated `*_pb2*` excluded) — `uv run ruff check .`. flake8 is gone.
- **mypy config lives in `[tool.mypy]`.** Do **NOT** re-create `mypy.ini` — it silently *shadows* the pyproject config. Generated `*_pb2*` modules get `ignore_errors` overrides.
- **Do NOT re-add `setup.py`** — with setuptools>=61 it conflicts with `[project]` on duplicated metadata.
- **PEP 625**: the sdist is now underscore-normalised (`ondewo_<name>-<v>.tar.gz`); anything that greps the tarball name by hand must use underscores.
- The version-bump release target edits the version in **pyproject.toml** (not setup.py); the release stages `pyproject.toml uv.lock`.
