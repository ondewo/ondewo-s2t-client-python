# Release History
*****************
## ONDEWO-S2T Python Client 3.1.2

### New Features
* Update grpcio libraries to versions 1.44.0.
* 
*****************
## ONDEWO-S2T Python Client 3.1.1

### New Features
* Update examples in examples/ondewo-s2t-wit-certificate.ipynb notebook.
* Add boolean registered_only option in ListS2tPipelinesRequest.

*****************
## ONDEWO-S2T Python Client 3.1.0

### New Features
* [[OND231-338]] -
Add mute_audio field in TranscribeStreamRequest.
  
## ONDEWO-S2T Python Client 3.0.0

### New breaking Features
* [[OND231-334]] -
Rename Description, GetServiceInfoResponse, Inference and Normalization messages to include S2T


## ONDEWO-S2T Python Client 2.0.0

### New breaking Features

* All configuration fields in the request messages TranscribeStreamRequest and TranscribeFileRequest have been replaced by a single configuration message TranscribeRequestConfig, which allows for more configuration possibilities, including changing the speech-to-text pipeline during streaming.
* Instead of a single transcription text of type string, the response messages TranscribeStreamResponse and TranscribeFileResponse now include a list (repeated field) of Transcription messages, each of which contains a transcription text (str) and a score (float).
* Update examples in _/example_s folder.

## ONDEWO-S2T Python Client 1.5.0

### New Features

* Compatible with ONDEWO-S2T 1.5.* GRPC server


## ONDEWO-S2T Python Client 1.4.1

### New Features

* added to the pypi


*****************

## ONDEWO-S2T Python Client 1.3.0

### New Features
 * First public version

### Improvements
 * Open source

### Known issues not covered in this release
 * CI/CD Integration is missing
 * Extend the README.md with an examples usage

