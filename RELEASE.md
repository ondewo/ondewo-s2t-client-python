# Release History

*****************

## Release ONDEWO S2T Python Client 7.4.2

### Bug Fixes

* [[OND221-2830]](https://ondewo.atlassian.net/browse/OND221-2830) Regenerated with [ondewo-proto-compiler 5.13.0](https://github.com/ondewo/ondewo-proto-compiler/releases/tag/5.13.0).
* [[OND221-2830]](https://ondewo.atlassian.net/browse/OND221-2830) Tooling: `conventional-pre-commit` now runs before `giticket` at the commit-msg stage - with giticket first, its `[OND221-2830] fix: ...` rewrite was no longer valid Conventional Commits and every commit on a ticket branch failed. `README.md` is prettier-ignored where `.prettierrc` sets `useTabs` and markdownlint's MD010 de-tabs the same blocks, and the codegen `docker run` invocations no longer pass `-it`, which fails outside a TTY.

*****************

## Release ONDEWO S2T Python Client 7.4.1

### Bug Fixes

* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **A client could silently authenticate as a different user.** `get_keycloak_token_provider` keyed its shared-provider registry on `id(config)` — the memory address of the `ClientConfig`. The service interfaces keep only the grpc channel, so the config passed to the usual `Client(config=ClientConfig(...))` becomes unreachable the moment the client is built; CPython then reuses that address for the next `ClientConfig`, and the `WeakValueDictionary` handed the new client the previous user's still-alive token provider. The second client authenticated as the first user — including when its own credentials were wrong or belonged to nobody at all. Any process that builds more than one client with different identities was affected, and the failure is silent: calls succeed, they are simply made as the wrong principal. The registry is now keyed by a SHA-256 of the credential set (`keycloak_url`, `realm`, `client_id`, username, `password`, `token_expiration_in_s`, `keycloak_verify_ssl`), so two configs share a provider exactly when a shared provider would behave identically for both, and never otherwise. The digest is hashed rather than stored as a plain tuple so the password does not end up in a module-level dict or in that frame's locals, where a traceback renderer printing locals would expose it. Same fix as `ondewo-nlu-client` 7.0.2 and `ondewo-csi-client` 5.4.1.
* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **`ClientConfig` printed its credentials in clear text.** `@dataclass` generates a `__repr__` that renders every field, so `log.debug(f"...{config}")` — or any traceback carrying locals — wrote the Keycloak `password` and the gRPC certificate to the logs. That is not hypothetical: a repository-wide sweep in ondewo-vtsi found this class among its leaking dataclasses, and the real staging password was observed on a developer console this way. `repr()` and `str()` now render `password` and `grpc_cert` as `***REDACTED***`. An unset or empty secret still renders as `None` / `''` rather than as the marker: `***REDACTED***` reads as "this is set and sensitive", which is actively misleading when the real fault is that nobody set it — usually the very thing being debugged.
* **Behaviour change** for anyone who parsed the repr: read the attribute (`config.password`, `config.grpc_cert`) instead. Only the rendered text changed — the fields themselves, equality and `dataclasses.asdict()` are untouched.

*****************

## Release ONDEWO S2T Python Client 7.4.0

### Improvements

* Tracking API Version [7.4.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/7.4.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 7.3.1

### Bug Fix

* [OND231-604](https://ondewo.atlassian.net/browse/OND231-604) Fix bugs in generate_services script.

*****************

## Release ONDEWO S2T Python Client 7.3.0

### Improvements

* Tracking API Version [7.3.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/7.3.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 7.2.0

### Improvements

* Tracking API Version [7.2.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/7.2.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 7.1.0

### Improvements

* Tracking API Version [7.1.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/7.1.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 7.0.0

### Improvements

* Tracking API Version [7.0.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/7.0.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 6.1.0

### Improvements

* Tracking API Version [6.1.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/6.1.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 6.0.0

### Improvements

* Tracking API Version [6.0.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/6.0.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.7.1

### Improvements

* Added functionality to pass grpc options to grpc clients based
  on [ONDEWO CLIENT UTILS PYTHON 2.0.0](https://github.com/ondewo/ondewo-client-utils-python/releases/tag/2.0.0)

*****************

## Release ONDEWO S2T Python Client 5.7.0

### Improvements

* Tracking API
  Version [5.7.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.7.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.6.0

### Improvements

* Tracking API
  Version [5.6.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.6.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.5.0

### Improvements

* Tracking API
  Version [5.5.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.5.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.4.0

### Improvements

* Tracking API
  Version [5.4.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.4.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.3.0

### Improvements

* Tracking API
  Version [5.3.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.3.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.2.0

### Improvements

* Tracking API
  Version [5.2.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.2.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.1.0

### Improvements

* Tracking API
  Version [5.1.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.1.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 5.0.0

### Improvements

* Tracking API
  Version [5.0.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/5.0.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 4.0.0

### Improvements

* Tracking API
  Version [4.0.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/4.0.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )

*****************

## Release ONDEWO S2T Python Client 3.4.0

### New Features

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) -Refactored automatic release
* Added endpoint to client for user language models

*****************

## Release ONDEWO S2T Python Client 3.3.0

### New Features

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) - Improved automated release process

*****************

## Release ONDEWO S2T Python Client 3.2.0

### New Features

* Proto complier introduced as submodule.
* Proto generation is dockerized.
* Libraries are updated.

*****************

## Release ONDEWO S2T Python Client 3.1.2

### New Features

* Delegate proto generation to ondewo-proto-compiler.

*****************

## Release ONDEWO S2T Python Client 3.1.1

### New Features

* Update examples in examples/ondewo-s2t-wit-certificate.ipynb notebook.
* Add boolean registered_only option in ListS2tPipelinesRequest.

*****************

## Release ONDEWO S2T Python Client 3.1.0

### New Features

* [[OND231-338]] -
  Add mute_audio field in TranscribeStreamRequest.

*****************

## Release ONDEWO S2T Python Client 3.0.0

### New breaking Features

* [[OND231-334]] -
  Rename Description, GetServiceInfoResponse, Inference and Normalization messages to include S2T

*****************

## Release ONDEWO S2T Python Client 2.0.0

### New breaking Features

* All configuration fields in the request messages TranscribeStreamRequest and TranscribeFileRequest have been replaced
  by a single configuration message TranscribeRequestConfig, which allows for more configuration possibilities,
  including changing the speech-to-text pipeline during streaming.
* Instead of a single transcription text of type string, the response messages TranscribeStreamResponse and
  TranscribeFileResponse now include a list (repeated field) of Transcription messages, each of which contains a
  transcription text (str) and a score (float).
* Update examples in _/example_s folder.

*****************

## Release ONDEWO S2T Python Client 1.5.0

### New Features

* Compatible with ONDEWO-S2T 1.5.* GRPC server

*****************

## Release ONDEWO S2T Python Client 1.4.1

### New Features

* added to the pypi

*****************

## Release ONDEWO S2T Python Client 1.3.0

### New Features

* First public version

### Improvements

* Open source

### Known issues not covered in this release

* CI/CD Integration is missing
* Extend the README.md with an examples usage

*****************
