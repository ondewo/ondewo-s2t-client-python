# How to become a contributor and submit your own code (WIP)

## Contributor License Agreements

We'd love to accept your sample apps and patches! Before we can take them, we
have to jump a couple of legal hurdles.

Please fill out either the individual or corporate Contributor License Agreement
(CLA).

* If you are an individual writing original source code and you're sure you
    own the intellectual property, then you'll need to sign an [individual CLA](TODO:).
* If you work for a company that wants to allow you to contribute your work,
    then you'll need to sign a [corporate CLA](TODO:).

Follow either of the two links above to access the appropriate CLA and
instructions for how to sign and return it. Once we receive it, we'll be able to
accept your pull requests.

## Contributing A Patch

1. Submit an issue describing your proposed change to the repo in question.
1. The repo owner will respond to your issue promptly.
1. If your proposed change is accepted, and you haven't already done so, sign a
   Contributor License Agreement (see details above).
1. Fork the desired repo, develop and test your code changes.
1. Ensure that your code adheres to the existing style in the sample to which
   you are contributing. Refer to the
   [Google Cloud Platform Samples Style Guide](https://cloud.google.com/community/tutorials/styleguide) for the
   recommended coding standards for this organization.
1. Ensure that your code has an appropriate set of unit tests which all pass.
1. Submit a pull request.

## Before You Submit

Every push runs the `tests` workflow (`.github/workflows/tests.yml`) on every branch, and a red run
blocks the change. Reproduce it locally with the workflow's own commands:

```bash
uv sync --extra dev --frozen
uv run --frozen ruff check .
uv run --frozen mypy ondewo
uv run --frozen pytest test/unit -q --cov --cov-report=term-missing --cov-fail-under=100
```

The coverage gate is enforced at **100%** over everything under `ondewo/` except the generated
`*_pb2.py` / `*_pb2_grpc.py` stubs, so a new file needs tests in the same change. `--frozen` is not
optional: it is how CI installs, and dropping it hides a stale `uv.lock`. After editing dependencies
in `pyproject.toml`, run `uv lock` and commit `uv.lock` alongside.

Also run the hooks over the whole tree before opening the pull request:

```bash
make precommit_hooks_run_all_files
```

Commit subjects are plain [Conventional Commits](https://www.conventionalcommits.org/) (`feat: …`,
`fix(scope): …`). Do **not** prepend the JIRA ticket yourself — the `giticket` hook reads it from the
branch name (`(feature|bugfix|support|hotfix)/OND<xxx>-<n>-…`) and adds the `[OND…]` prefix for you.
