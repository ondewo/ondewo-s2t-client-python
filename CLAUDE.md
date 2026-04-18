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
