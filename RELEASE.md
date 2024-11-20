# Release History

*****************
## Release ONDEWO S2T Python Client 6.1.0

### Improvements
 * Tracking API Version [6.1.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/6.1.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )


*****************
## Release ONDEWO S2T Python Client 6.0.0

### Improvements
 * Tracking API Version [6.0.0](https://github.com/ondewo/ondewo-s2t-api/releases/tag/6.0.0) ( [Documentation](https://ondewo.github.io/ondewo-s2t-api/) )


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

## Release ONDEWO S2T Python Client 3.0.0

### New breaking Features

* [[OND231-334]] -
  Rename Description, GetServiceInfoResponse, Inference and Normalization messages to include S2T

## Release ONDEWO S2T Python Client 2.0.0

### New breaking Features

* All configuration fields in the request messages TranscribeStreamRequest and TranscribeFileRequest have been replaced
  by a single configuration message TranscribeRequestConfig, which allows for more configuration possibilities,
  including changing the speech-to-text pipeline during streaming.
* Instead of a single transcription text of type string, the response messages TranscribeStreamResponse and
  TranscribeFileResponse now include a list (repeated field) of Transcription messages, each of which contains a
  transcription text (str) and a score (float).
* Update examples in _/example_s folder.

## Release ONDEWO S2T Python Client 1.5.0

### New Features

* Compatible with ONDEWO-S2T 1.5.* GRPC server

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
