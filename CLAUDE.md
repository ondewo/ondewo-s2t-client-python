# CLAUDE.md — ONDEWO S2T Python Client

## Project Overview

This is the official Python client library for the **ONDEWO Speech-to-Text (S2T)** gRPC service.
It exposes both a synchronous (`Client`) and an asynchronous (`AsyncClient`) interface, each backed
by a generated service wrapper (`Speech2Text`) that delegates directly to the gRPC stub.

**Package name:** `ondewo-s2t-client`
**Current version:** `7.4.2` — held in three places that must agree: `pyproject.toml` `version`,
`Makefile` `ONDEWO_S2T_VERSION`, and the newest `## Release … <VERSION>` heading in `RELEASE.md`.
`make update_setup` copies the Makefile value into `pyproject.toml`.
**Python:** `requires-python = ">=3.9"`; CI runs 3.12.

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
    services_interface.py      # Sync  service base (auth metadata lives here)
    async_services_interface.py# Async service base
    utils/
      keycloak.py              # D18 headless offline-token provider (hand-written, security-critical)
  scripts/
    generate_services.py       # Code-generator: reads proto → writes service wrappers
  py.typed                     # PEP 561 marker; without it the shipped .pyi stubs are ignored
  speech_to_text_pb2.py        # Generated protobuf message classes
  speech_to_text_pb2_grpc.py   # Generated gRPC stub classes
examples/
  file_transcription_example.py
  streaming_example.py
  ondewo-s2t-with-certificate.ipynb
  audiofiles/                  # sample_1.wav, sample_2.wav
test/
  unit/
    conftest.py                          # Shared pytest fixtures
    test_sync_client.py                  # Sync client & service wrapper
    test_async_client.py                 # Async client & service wrapper
    test_services_interface.py           # Auth-metadata plumbing on both interfaces
    test_client_config_redacts_secrets.py# ClientConfig __repr__ redaction
    test_keycloak.py                     # Offline-token provider (login/refresh/registry/teardown)
    test_generate_services.py            # The code generator itself
    test_examples.py                     # The examples/ scripts still import and parse
```

Note `test/` is **singular** here (`ondewo-t2s-client-python` and `ondewo-nlu-client-python` use
`tests/`); `pytest.ini` sets `testpaths = test` and the workflow says `pytest test/unit`.

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

- [`uv`](https://docs.astral.sh/uv/) (the Makefile installs it if missing)
- `make`, `git`, and `docker` for the codegen/release targets only

**There is no conda here.** `requirements.txt`, `requirements-dev.txt`, `setup.py`, `setup.cfg` and
`mypy.ini` were all deleted in the uv migration — do not re-create them; dependency and tool config
lives in `pyproject.toml` with a committed `uv.lock`.

```bash
make setup_developer_environment_locally   # install uv → uv sync --extra dev → pre-commit install (both stages)
```

That is `install_uv` + `uv sync --extra dev` + `uv run pre-commit install` and
`uv run pre-commit install --hook-type commit-msg`. The commit-msg stage matters: `giticket` and
`conventional-pre-commit` only run there.

---

## Running Tests

```bash
make test                                       # full suite + the 100% coverage gate (HTML report too)
make test_unit                                  # suite only, no coverage
uv run --frozen pytest test/unit/test_keycloak.py -q     # one file
uv run --frozen pytest test/unit -q -k keycloak          # one selection
```

Tests use `pytest-asyncio` (`asyncio_mode = auto` in `pytest.ini`, so no `@pytest.mark.asyncio`) and
mock all gRPC infrastructure — no running S2T server is required. `pytest.ini` sets `addopts = -v`,
so pass `-q` when you want the short form.

### The coverage gate

Scope lives in `pyproject.toml`, **not** on the command line:

- `[tool.coverage.run] source = ["ondewo"]` — a **filesystem** scan. This is the whole point. The
  gate used to enumerate dotted `--cov=ondewo.s2t.client.…` targets, and pytest-cov only measures a
  dotted module the suite actually **imports**, so a file with no tests was dropped from the report
  instead of scored 0%. It printed "Required test coverage of 100% reached" while
  `ondewo/s2t/scripts/generate_services.py` (250 statements) was never measured at all. Measured
  surface went from 222 to 623 statements when this was fixed.
- `omit` is only the generated `*_pb2.py` / `*_pb2_grpc.py` stubs. Nothing hand-written is omitted.
- `[tool.coverage.report] include_namespace_packages = true` is **required**: `ondewo/s2t/scripts/`
  has no `__init__.py`, so coverage's package walk skips the whole directory without it — the same
  fail-open shape by a different route. The option belongs under `[report]`; under `[run]` coverage
  emits `CoverageWarning: Unrecognized option` and silently ignores it.
- Verify the gate still fails closed after touching any of this: drop a throwaway
  `ondewo/s2t/client/_probe.py` with one uncovered statement, run the gate, and confirm it exits 1.

---

## Code Generation

The service wrappers are generated from the proto definitions in the `ondewo-s2t-api` submodule.

```bash
make build                  # clear → init/checkout submodules → build compiler image → protos → services → version
make generate_ondewo_protos # protoc via the ondewo-proto-compiler docker image
make generate_services      # runs ondewo/s2t/scripts/generate_services.py (sync AND async in one pass)
make create_async_services  # perl rewrite of services/*.py into services/async_*.py (legacy path)
```

`generate_services.py` emits the async variants itself (`for_async=True`), so `create_async_services`
is only needed for a service directory the generator did not produce.

**Do not edit** the following files manually — they will be overwritten:

- `ondewo/s2t/client/client.py`
- `ondewo/s2t/client/async_client.py`
- `ondewo/s2t/client/services_container.py`
- `ondewo/s2t/client/async_services_container.py`
- `ondewo/s2t/client/services/speech_to_text.py`
- `ondewo/s2t/client/services/async_speech_to_text.py`

---

## Submodules — `ondewo-s2t-api` and `ondewo-proto-compiler`

Both are git submodules pinned twice over: by the **gitlink** committed in this repo, and by a
**Makefile variable** that `make checkout_defined_submodule_versions` checks out over it. The two
can disagree, and when they do the Makefile wins at build time and silently moves the submodule.

| Submodule | Makefile variable | Current value |
| --------- | ----------------- | ------------- |
| `ondewo-s2t-api` | `ONDEWO_S2T_API_GIT_BRANCH` | `OND211-2418-add-keycloak-for-2-fa` (a **branch**, not a tag) |
| `ondewo-proto-compiler` | `ONDEWO_PROTO_COMPILER_GIT_BRANCH` | `tags/5.14.0` |

### Bumping the proto-compiler pin

It is exactly two edits, and **never** a regeneration:

```bash
git submodule update --init --recursive
git -C ondewo-proto-compiler fetch --tags origin
git -C ondewo-proto-compiler checkout <VERSION>          # moves the gitlink
perl -i -pe 's|^ONDEWO_PROTO_COMPILER_GIT_BRANCH=.*|ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/<VERSION>|' Makefile
git add ondewo-proto-compiler Makefile
git submodule status | grep proto-compiler               # must print the new tag
```

- The canonical `ondewo-proto-compiler/update_proto_compiler_dependency.sh` also syncs
  `src/package.json` dependencies and a `Dockerfile.utils` `NODE_VERSION`. **Neither applies here**:
  this is a Python client with no `src/package.json`, and `Dockerfile.utils` is
  `FROM python:3.12-slim` with no `NODE_VERSION` line. Only the two edits above are in scope.
- A pin bump changes which image `make build` would build. It **rewrites no committed stub.**
  `git diff --stat 5.11.0..5.14.0 -- python/` in the compiler repo is empty — 5.12.0/5.13.0/5.14.0
  are entirely Angular/JS/Node/TS fixes, so for this repo the bump is pin hygiene with zero
  behavioural content. Do **not** write "Regenerated with ondewo-proto-compiler X" in `RELEASE.md`
  unless stubs were actually regenerated; word it as "Pinned …".
- **Known inconsistency, do not silently "fix":** the already-released `RELEASE.md` 7.4.2 entry says
  "Regenerated with ondewo-proto-compiler 5.13.0" while the pin at that tag was 5.12.0.

---

## Key Makefile Targets

| Target | Description |
| -------- | ------------- |
| `make test` | Unit tests + the 100% coverage gate, terminal + `htmlcov/` report |
| `make test_unit` | Unit tests only, no coverage |
| `make ruff` / `make ruff_fix` / `make ruff_format` | Lint / lint-and-fix / format (there is **no** `flake8` target) |
| `make mypy` | Type-check `ondewo/` **and** `test/` (the CI step only checks `ondewo`) |
| `make precommit_hooks_run_all_files` | `uv run --extra dev pre-commit run --all-files` |
| `make generate_services` | Regenerate the service wrappers from the protos |
| `make build` | Full build (submodules → compiler image → protos → services → `update_setup`) |
| `make setup_developer_environment_locally` | uv + `.venv` + pre-commit hooks |
| `make TEST` | Print release variables — token values are masked as `<set>`/`<unset>` |

---

## Release Process

1. Update `ONDEWO_S2T_VERSION` in `Makefile`
2. Add a `## Release ONDEWO S2T Python Client <VERSION>` section to `RELEASE.md`, terminated by the
   `*****************` separator — `CURRENT_RELEASE_NOTES` slices between exactly those two markers
   (`perl -ne 'print if /Release ONDEWO S2T Python Client <VERSION>/../^\*{5}/'`), so a missing
   separator swallows the rest of the file and a renamed heading yields empty release notes
3. Run `make update_setup` — it bumps `version` in **`pyproject.toml`** (there is no `setup.py`)
4. Run `make ondewo_release` (clones `ondewo-devops-accounts` for credentials)

`make spc` guards the release: it refuses to start if the release branch or tag already exists. Its
third check (pyproject version vs `ONDEWO_S2T_VERSION`) is commented out — dead code, so the version
consistency in the header above is on you.

---

## Notes for Claude

- **Service files are auto-generated** — suggest edits to `generate_services.py` instead. That
  generator is itself gated at 100% by `test/unit/test_generate_services.py`, so changing it means
  changing those tests too.
- **The `stub` property is non-cached** — patch `Speech2TextStub` at the module level in tests.
- **asyncio_mode = auto** is set in `pytest.ini` — async test functions do not need
  `@pytest.mark.asyncio`.
- **Every command goes through `uv run --frozen`** (or `make`). There is no conda env and no
  `pip install`; `.venv` is created by `uv sync --extra dev`.
- The `.gitignore` tracks `.vscode/` explicitly — vscode config files use git `force-add` or the
  gitignore exemptions at the bottom of the file.
- **Known dead code, left deliberately** (do not "clean up" without a ticket):
  `proto_stem_to_file_name` in `generate_services.py` returns `stem` unconditionally, so its
  `y -> ies` / `+s` pluralisation rules below the return are unreachable (marked `# pragma: no
  cover`, and its docstring still describes the dead behaviour); and `make spc`'s
  `pyproject_version` check is commented out.

---

## Python 3.9 Compatibility

All generated and hand-written code **must be compatible with Python 3.9**. Enforce these rules:

- **No `X | Y` union syntax** — use `Union[X, Y]` from `typing` instead.
- **No `list[...]`, `dict[...`, `tuple[...]` as generic type hints** — use `List`, `Dict`, `Tuple`
  from `typing` instead (built-in generics require Python 3.9+ only for runtime use; the `from
  __future__ import annotations` trick avoids the issue but is not required here — just use `typing`).
- **No `match`/`case` statements** — added in Python 3.10.
- **No `TypeAlias` or `ParamSpec`** without a `typing_extensions` fallback.
- **`str.removeprefix` / `str.removesuffix` are fine** — both landed in Python 3.9.
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

- **Trust the registry, not the log.** `make release_all_clients` wraps each client in `|| echo "Already released …"`, so a _failed_ release is reported as "done". After any release, verify the GitHub release **and** the published package (PyPI / npm) directly.
- **`npm install failed after 5 attempts` in a release log is usually a red herring** — that text is the echo _inside_ the docker `RUN for i in 1..5; do npm install …` retry loop, not a real failure (`npm install` succeeds → `#10 DONE`). Look further down for the real error (a TTY error, an eslint failure, a `setup.py` error).
- **Codegen must run TTY-free.** The `docker run` that invokes the proto-compiler must not pass `-it` — non-interactively it fails with `cannot attach stdin to a TTY-enabled container because stdin is not a terminal`. Fix the script (drop `-it`), or run the whole release under a pseudo-TTY: `script -qc 'make …' /dev/null`.
- **Release Makefiles print secrets.** Some `docker run … -e <TOKEN>=…` recipe lines lack a leading `@`, so `make` echoes the expanded token. Rotate any token printed during a release; fix by prefixing the recipe line with `@`.
- **The release does NOT pull the latest `ondewo-proto-compiler` tag.** `make build` runs
  `checkout_defined_submodule_versions`, which checks out `ONDEWO_PROTO_COMPILER_GIT_BRANCH`
  (`tags/5.14.0`) — the pin, not `master`. See the proto-compiler section below.
- **npm package names are inconsistent** — e.g. the JS client publishes as `@ondewo/ondewo-nlu-client-js` (double `ondewo`), not `@ondewo/nlu-client-js`. Check `src/package.json`'s `name` before querying npm.
- **PyPI build needs setuptools.** The release image (`Dockerfile.utils`) is `python:3.12-slim`, which bundles no `setuptools`, so `python setup.py sdist bdist_wheel` dies with `ModuleNotFoundError: No module named 'setuptools'`. `Dockerfile.utils` must `pip install … setuptools wheel`.

## Python tooling — uv + ruff + mypy + pyproject.toml (this session's refactor)

This repo was migrated off `setup.py` / `.flake8` / `mypy.ini` to a single **pyproject.toml** with **uv**, **ruff**, and **mypy**. Going forward:

- **Build backend stays setuptools** (for PyPI compatibility). Build with `python -m build --no-isolation` or `uv build` — NOT `python setup.py sdist bdist_wheel` (setup.py is deleted). `Dockerfile.utils` installs `twine setuptools wheel build`.
- **Dependencies via uv + a committed `uv.lock`.** CI runs `uv sync --extra dev --frozen`. To add/change a dep: edit `[project.dependencies]`/`[project.optional-dependencies].dev` in pyproject.toml then `uv lock`.
- **Lint is ruff** (`[tool.ruff]`, line-length 120, generated `*_pb2*` excluded) — `uv run ruff check .`. flake8 is gone.
- **mypy config lives in `[tool.mypy]`.** Do **NOT** re-create `mypy.ini` — it silently _shadows_ the pyproject config. Generated `*_pb2*` modules get `ignore_errors` overrides.
- **Do NOT re-add `setup.py`** — with setuptools>=61 it conflicts with `[project]` on duplicated metadata.
- **PEP 625**: the sdist is now underscore-normalised (`ondewo_<name>-<v>.tar.gz`); anything that greps the tarball name by hand must use underscores.
- The version-bump release target edits the version in **pyproject.toml** (not setup.py); the release stages `pyproject.toml uv.lock`.

### Packaging invariants

- **`[project.dependencies]` is deliberately minimal**: `grpcio`, `ondewo-client-utils>=3.2.0`,
  `protobuf`, `requests`. An import scan over `ondewo/` and `examples/` finds nothing else beyond
  the stdlib and `urllib3` (which arrives with `requests`). `grpcio-reflection`, `grpcio-tools`,
  `regex` and `setuptools` were declared and never imported — codegen runs in the proto-compiler
  docker image, not from this package. (`grpc_reflection` / `grpc_tools` show up in `sys.modules`
  after `import grpc` only because grpc's `_runtime_protos.py` probes for them behind `try/except`;
  presence is not use.) `setuptools` stays in `[build-system].requires`, a different consumer.
- **Do not `import dataclasses_json` anywhere.** `ClientConfig` is a plain `@dataclass(frozen=True)`
  subclass of `BaseClientConfig`, and it inherits `to_dict`/`from_dict`/`to_json` because
  `ondewo-client-utils` 3.2.0 decorates the base. The package was previously importing
  `dataclasses_json` without declaring it, riding on that transitive chain — which client-utils
  3.3.0 drops, so the SDK would have become unimportable the moment 3.3.0 hit PyPI. Raise the floor
  to `>=3.3.0` once it ships.
- **`ondewo/s2t/py.typed` must exist** (empty file). `pyproject.toml`'s `package-data` and
  `MANIFEST.in` have always listed it, but the file itself was missing, so PEP 561 consumers ignored
  the bundled `speech_to_text_pb2.pyi` entirely.

## uv migration — completed conversion (this session)

The repo is now fully on **uv** (not just pyproject.toml):

- `make setup_developer_environment_locally` bootstraps uv (installs it if missing), runs `uv sync --extra dev` (creates `.venv` + installs all runtime+dev deps + pre-commit), then `uv run pre-commit install`. **No conda** — the old `create_conda_env`/`setup_conda_env` scaffolding was removed.
- Every Makefile target uses uv: `uv sync --extra dev` (deps), `uv run pytest`/`ruff`/`mypy` (tools), `uv build` (wheel). No `pip install`, no `python -m build`, no `python setup.py`.
- New targets: `make ruff` / `make ruff_fix` / `make ruff_format` / `make mypy`. The `flake8` target is **removed**.
- Removed for good: `requirements.txt`, `requirements-dev.txt`, `setup.cfg` — deps + tool config live in `pyproject.toml`. Do **not** re-add them.
- `Dockerfile.utils` installs uv (`COPY --from=ghcr.io/astral-sh/uv`) and builds with uv; it no longer `COPY`s `requirements.txt`.
- **`[tool.mypy] python_version` is `3.10` here** — the oldest value mypy 2.x accepts, while
  runtime support still spans 3.9–3.12 via `requires-python`. (The fleet-wide rule that it must
  be `3.12` applies only where numpy 2.x is on the mypy path, whose PEP-695 stubs fail to parse
  below 3.12. This repo has no numpy dependency, so 3.10 is correct — do not "align" it.)
- The release `git commit` uses **`--no-verify`** so pre-commit hooks never gate an automated release.
- **Validated by a real PyPI publish** — `ondewo-t2s-client 6.5.0` was built with `uv build` and uploaded via twine end-to-end; the uv release pipeline works.

## GitHub Actions — the `tests` workflow is a required gate

`.github/workflows/tests.yml` (job `unit-tests`) runs on **every push to every branch** (`branches: ["**"]`)
and on every pull request. It is a **gate, not advisory**: a red run is a broken commit, so run it
locally _before_ pushing rather than discovering it on GitHub.

**Reproduce it locally with the workflow's exact commands** — copy them from `tests.yml`, do not
approximate them:

```bash
uv python install 3.12
uv sync --extra dev --frozen
uv run --frozen ruff check .
uv run --frozen mypy ondewo
uv run --frozen pytest test/unit -q \
  --cov \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=100
```

- **Keep `--frozen` on every command.** Without it `uv` silently re-resolves and installs whatever
  is newest, so a **stale `uv.lock` passes locally and fails in CI** — CI always runs frozen. The
  `Makefile` targets (`make test`, `make ruff`, `make mypy`) are _not_ the gate: they run without
  `--frozen`, so a green `make test` is not evidence the workflow is green. After any
  `pyproject.toml` dependency edit, run `uv lock` and commit `uv.lock` in the same commit.
- **The coverage step is a bare `--cov` on purpose — never re-introduce dotted `--cov=<module>`
  arguments.** That form fails OPEN: pytest-cov only measures a dotted module the suite actually
  **imports**, so a file nothing imports is dropped from the report instead of scored 0%. This repo
  shipped that bug: `ondewo/s2t/scripts/generate_services.py` (250 statements, no tests) never
  appeared in the table while the step printed "Required test coverage of 100% reached" and exited
  0. The scope now lives in `pyproject.toml` `[tool.coverage.run] source = ["ondewo"]` (see _The
  coverage gate_ above), so a new untested file makes the step red.
- **`uv python install 3.12` pins nothing.** There is no `.python-version`, and `requires-python`
  is `>=3.9`, so `uv sync` builds `.venv` on whatever compatible interpreter it discovers first — a
  fresh `uv sync --extra dev --frozen` here selects **CPython 3.14.6** while CI runs on 3.12. Both
  are green today, but a passing local run says nothing about CI's interpreter. Check
  `.venv/pyvenv.cfg` before blaming a version-specific failure on the code.
- **`ruff check .` and `mypy ondewo` have different scopes.** ruff lints the whole tree (generated
  `*_pb2*`, the two submodules and `*.ipynb` are excluded via `[tool.ruff] extend-exclude`); mypy is
  pointed at the `ondewo` package only, so nothing under `test/` or `examples/` is type-checked by
  the gate. A type error in a test file is invisible to CI.
- **The pytest step writes `coverage.xml` into the repo root.** It is gitignored; do not commit it.
- **Confirm a real run rather than assuming.** `gh` may be installed but unauthenticated (no
  token), in which case use the token-free public REST API — verified reachable, HTTP 200:

  ```bash
  SHA=$(git rev-parse HEAD)
  curl -s "https://api.github.com/repos/ondewo/ondewo-s2t-client-python/actions/runs?head_sha=$SHA"
  ```

  Read `.workflow_runs[].status` / `.conclusion`; append `/jobs` to a run's API URL for the
  per-step conclusions. The repo is public, so these endpoints need no token.

## Pre-commit — the commit-msg hook ORDER is load-bearing

`conventional-pre-commit` **must stay declared before `giticket`.** Both run at the `commit-msg`
stage and pre-commit runs them in declaration order. `giticket` rewrites the subject to
`[OND231-624] feat: …`, which is no longer valid Conventional Commits, so a validator running
_after_ it rejects every commit on a ticket branch. Validate first, decorate second.

This repo carried the block **twice** — correctly before `giticket` and again after it — which made
the earlier reorder a no-op. Only one block may exist. Probe it for real rather than reasoning about
it: on a branch named `feature/OND231-624-probe`, `git commit -m "feat: x"` must print
`Conventional Commit … Passed` then `giticket … Passed` and land as `[OND231-624] feat: x`.

Consequences for anyone committing here: write plain Conventional Commits subjects and let
`giticket` add the prefix (see _Git Commits_ above).

### Hook versions

| Hook | rev | Note |
| ---- | --- | ---- |
| `markdownlint-cli2` | `v0.23.2` | v0.23.0's `applyFix` crashes with `TypeError … reading 'slice'` on some markdown |
| `ruff-pre-commit` | `v0.16.6` | must match the `ruff` pin in `uv.lock`, which is what CI runs |
| `mirrors-mypy` | `v2.3.1` | **cosmetic**: the hook is `language: system`, so `uv.lock`'s mypy is the real pin |
| `pre-commit-hooks` | `v6.0.0` | already newest |
| `uv-pre-commit` | `0.12.10` | **no leading `v`** — that is the actual tag spelling |
| `conventional-pre-commit` | `v4.4.0` | already newest stable; the later `-pre1` tags are pre-releases of released versions |
| `giticket` | `'1.92'` | already newest; **keep it quoted** — unquoted `1.92` is a YAML float |

After bumping `ruff-pre-commit` or `mirrors-mypy`, bump the lock too
(`uv lock --upgrade-package ruff --upgrade-package mypy`), or the hook and the CI gate silently run
different versions.

### Sharp edges

- **Never run `uvx pre-commit run --all-files` here.** The `mypy` hook is `language: system`
  (deliberately, so it sees the `types-*` packages), so pre-commit resolves `mypy` from `PATH`; an
  ephemeral `uvx` environment has none and the hook fails with "Executable `mypy` not found" — a
  false red. Use `uv run --frozen pre-commit run --all-files` or `make precommit_hooks_run_all_files`
  (`PATH="$PWD/.venv/bin:$PATH" uvx pre-commit …` also works, if you must use `uvx`).
- **`MD053` must stay `false`** in `.markdownlint-cli2.yaml`: its auto-fix deletes the
  `[comment]: <>` reference-definition markers the release tooling greps for. `markdownlint-cli2`
  runs with `fix: true`, so it _will_ rewrite committed markdown — commit those rewrites.
- **`RELEASE.md` survives markdownlint intact** — it only strips trailing whitespace and adjusts
  blank lines around headings; the `## Release … <VERSION>` headings and the `*****************`
  separators `CURRENT_RELEASE_NOTES` depends on are untouched. Re-check that after any rev bump.
- **ruff 0.16 claims Markdown.** `ruff-format`'s `types_or` gained `markdown`, so the hook now
  formats python code blocks inside `*.md`. It is a no-op on this repo's markdown today, but expect
  it to start touching README/CLAUDE code fences.
- ruff 0.16 also enables 413 rules by default instead of 59. Irrelevant here — `[tool.ruff.lint]`
  sets `select = ["E", "F", "W"]` explicitly, so the default set is never consulted. Do **not**
  adopt the new default set. The `ruff` hook id still works but is now labelled a legacy alias for
  `ruff-check`.

## Jenkins — never trigger a multibranch scan or branch indexing

**NEVER trigger a Jenkins multibranch scan or branch indexing.** Do not call a multibranch/folder job's
`build`, `scan`, or reindex endpoints, click "Scan Repository Now" / "Build Now" on a folder, run
`p4 scan`, or use any API/CLI that reindexes branches or scans the repository. A scan/reindex runs across
**every** branch, consumes CI resources, and can kick off unintended builds and deploys.

If a branch is not building — it was not discovered, or its job is marked `buildable: false` / orphaned —
**report it and stop**. Let the user or a Jenkins admin adjust branch-discovery/config or rename the branch
to the convention. Never force a build by scanning or reindexing.
