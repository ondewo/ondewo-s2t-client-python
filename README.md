<div align="center">
  <table>
    <tr>
      <td>
        <a href="https://ondewo.com/en/products/natural-language-understanding/">
            <img width="400px" src="https://raw.githubusercontent.com/ondewo/ondewo-logos/master/ondewo_we_automate_your_phone_calls.png"/>
        </a>
      </td>
    </tr>
    <tr>
        <td align="center">
          <a href="https://www.linkedin.com/company/ondewo "><img width="40px" src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png"></a>
          <a href="https://www.facebook.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
          <a href="https://twitter.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733579.png"> </a>
          <a href="https://www.instagram.com/ondewo.ai/"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/174/174855.png"></a>
        </td>
    </tr>
  </table>
  <h1>
  Ondewo S2T Client Python Library
  </h1>
</div>

This library facilitates the interaction between a user and a CAI server. It achieves this by providing a higher-level interface mediator.

This higher-level interface mediator is structured around a series of python files generated from protobuf files. These protobuf files specify the details of the interface, and can be used to generate code in 10+ high-level languages. They are found in the [ONDEWO S2T API](https://github.com/ondewo/ondewo-s2t-api) along with the older Google protobufs from Dialogueflow that were used at the start. The [ONDEWO PROTO-COMPILER](https://github.com/ondewo/ondewo-proto-compiler) will generate the needed files directly in this library.

## Python Installation

You can install the library by installing it directly from the PyPi:

```bash
pip install ondewo-s2t-client
```

Or, you could clone it and install the requirements:

```bash
git clone git@github.com:ondewo/ondewo-s2t-client-python.git
cd ondewo-s2t-client-python
make setup_developer_environment_locally
```

## Repository Structure

```
.
├── examples               <----- Helpful for implementation of code
│   ├── audiofiles
│   │   ├── sample_1.wav
│   │   └── sample_2.wav
│   ├── configs
│   │   ├── insecure_grpc.json
│   │   └── secure_grpc_placeholder.json
│   ├── lm_data
│   │   └── shakespeare.zip
│   ├── file_transcription_example.py
│   ├── ondewo-s2t-with-certificate.ipynb
│   └── streaming_example.py
├── ondewo
│   ├── s2t
│   │   ├── client
│   │   │   ├── services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── async_speech_to_text.py
│   │   │   │   └── speech_to_text.py
│   │   │   ├── utils
│   │   │   │   ├── __init__.py
│   │   │   │   └── keycloak.py           <----- D18 Keycloak headless offline-token provider
│   │   │   ├── __init__.py
│   │   │   ├── async_client.py
│   │   │   ├── async_services_container.py
│   │   │   ├── async_services_interface.py
│   │   │   ├── client.py
│   │   │   ├── client_config.py
│   │   │   ├── services_container.py
│   │   │   └── services_interface.py
│   │   ├── __init__.py
│   │   ├── speech_to_text_pb2_grpc.py
│   │   ├── speech_to_text_pb2.py
│   │   └── speech_to_text_pb2.pyi
│   └── __init__.py
├── ondewo-proto-compiler           <----- @ https://github.com/ondewo/ondewo-proto-compiler
├── ondewo-s2t-api                  <----- @ https://github.com/ondewo/ondewo-s2t-api
├── CONTRIBUTING.md
├── Dockerfile.utils
├── LICENSE
├── Makefile
├── mypy.ini
├── README.md
├── RELEASE.md
├── requirements-dev.txt
├── requirements.txt
├── setup.cfg
└── setup.py

```

## Build

The `make build` command is dependent on 2 `repositories` and their speciefied `version`:

- [ondewo-s2t-api](https://github.com/ondewo/ondewo-s2t-api) -- `S2T_API_GIT_BRANCH` in `Makefile`
- [ondewo-proto-compiler](https://github.com/ondewo/ondewo-proto-compiler) -- `ONDEWO_PROTO_COMPILER_GIT_BRANCH` in `Makefile`

It will generate a `_pb2.py`, `_pb2.pyi` and `_pb2_grpc.py` file for every `.proto` in the api submodule.

> :warning: All Files in the `ondewo` folder that dont have `pb2` in their name are handwritten, and therefor need to be manually adjusted to any changes in the proto-code.

## Examples

The `/examples` folder provides a possible implementation of this library. To run an example, simply execute it like any other python file and point it at a JSON config with `--config` (see `examples/configs/`). The config is parsed into `ondewo.s2t.client.client_config.ClientConfig` and supports the following fields:

- host `// The hostname of the server - e.g. 127.0.0.1`
- port `// Port of the server - e.g. 6600`
- grpc_cert `// gRPC certificate of the server (required for a secure channel)`
- keycloak_url `// Base URL of the Keycloak server (optional headless-auth parameter)`
- realm `// Keycloak realm (optional headless-auth parameter)`
- client_id `// Public Keycloak client id, no secret (optional headless-auth parameter)`
- user_name `// Technical-user email/username for the Keycloak ROPC grant (optional)`
- password `// Technical-user password (optional)`

A bare `{"host": ..., "port": ...}` config (as in `examples/configs/insecure_grpc.json`) stays valid for an unauthenticated / ingress-injected-auth server; the Keycloak fields are only required together when any one of them is set.

## Authentication (Keycloak bearer)

When the config carries the Keycloak fields, the SDK authenticates headlessly against a **public** Keycloak client (no client secret — D18/Q1) using the offline-token flow: a one-time Resource Owner Password Credentials login (`grant_type=password` with `scope=offline_access`) yields a long-lived offline refresh token, and the client then auto-refreshes a short-lived access token in the background before it expires. The technical user is 2FA-exempt (D14), so ROPC bypasses the browser flow.

`Client` and `AsyncClient` forward this token automatically: every RPC issued through the service wrappers travels with the canonical gRPC metadata `Authorization: Bearer <jwt>`, so application code never has to build or refresh the header itself. A config without the Keycloak fields sends no such header and calls travel unauthenticated (e.g. against a plaintext server or an Envoy ingress that injects auth).

## Automatic Release Process

The entire process is automated to make development easier. The actual steps are simple:

TODO after Pull Request was merged in:

- Checkout master:

  ```shell
  git checkout master
  ```

- Pull the new stuff:

  ```shell
  git pull
  ```

- (If not already, run the `setup_developer_environment_locally` command):

  ```shell
  make setup_developer_environment_locally
  ```

- Update the `ONDEWO_S2T_VERSION` in the `Makefile`
- Add the new Release Notes in `RELEASE.md` in the format:

  ```
  ## Release ONDEWO S2T Python Client X.X.X       <---- Beginning of Notes

     ...<NOTES>...

  *****************                      <---- End of Notes
  ```

- Release:

  ```shell
  make ondewo_release
  ```

---

The release process can be divided into 6 Steps:

1. `build` specified version of the `ondewo-s2t-api`
2. `commit and push` all changes in code resulting from the `build`
3. Create and push the `release branch` e.g. `release/1.3.20`
4. Create and push the `release tag` e.g. `1.3.20`
5. Create a new `Release` on GitHub
6. Publish the built `dist` folder to `pypi.org`

> :warning: The Release Automation checks if the build has created all the proto-code files, but it does not check the code-integrity. Please build and test the generated code prior to starting the release process.
