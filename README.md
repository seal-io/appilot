# Appilot

Appilot['æpaɪlət] stands for application-pilot.
It is an experimental project that helps you operate applications using GPT-like LLMs.

## Feature

- Application management: deploy, upgrade, rollback, etc.
- Environment management: clone, view topology, etc.
- Diagnose: view logs, find flaws and provide fixes.
- Safeguard: any action involving state changes requires human approval.
- Hybrid infrastructure: works on kubernetes, VM, cloud, on-prem.
- Multi language support: It's not restricted to a specific natural language. Choose the one you're comfortable with.
- Pluggable backends: It supports multiple backends including Walrus and Kubernetes, and is extensible.

## Demo

Chat to deploy llama-2 on AWS:

https://github.com/seal-io/appilot/assets/5697937/0562fe29-8e97-42ba-bbf6-eaa5b5fefc41

Other use cases:

- [Manage applications in Kubernetes using helm charts](./examples/k8s_helm.md)
- [Operating native Kubernetes resources](./examples/k8s_yaml.md)
- [Diagnose and fix issues](./examples/k8s_diagnose.md)

## Quickstart

> **prerequistes:**
>
> - Get OpenAI API key with access to the gpt-4 model.
> - Install `python3` and `make`.
> - Install [kubectl](https://kubernetes.io/docs/tasks/tools/) and [helm](https://helm.sh/docs/intro/install/).
> - Have a running Kubernetes cluster.

1. Clone the repository.

```
git clone https://github.com/seal-io/appilot && cd appilot
```

2. Run the following command to get the envfile.

```
mv .env.example .env
```

3. Edit the `.env` file and fill in `OPENAI_API_KEY`.

4. Run the following command to install. It will create a venv and install required dependencies.

```
make install
```

5. Run the following command to get started:

```
make run
```

6. Ask Appilot to deploy an application, e.g.:

```
Deploy a jupyterhub.
```

## Usage

### Configuration

Appilot is configurable via environment variable or the envfile:
| Parameter | Description | Default |
|----------|------|---------------|
| OPENAI_API_KEY | OpenAI API key, access to gpt-4 model is required. | "" |
| OPENAI_API_BASE | Custom openAI API base. You can integrate with other LLMs as long as they serve in the same API style. | "" |
| TOOLKITS | Toolkits to enable. Currently support Kubernetes and Walrus. Case insensitive. | "kubernetes" |
| NATURAL_LANGUAGE | Natural language AI used to interacte with you. e.g., Chinese, Japanese, etc. | "English" |
| SHOW_REASONING | Show AI reasoning steps. | True |
| VERBOSE | Output in verbose mode. | False |
| WALRUS_URL | URL of Walrus, valid when Walrus toolkit is enabled. | "" |
| WALRUS_API_KEY | API key of Walrus, valid when Walrus toolkit is enabled. | "" |
| WALRUS_SKIP_TLS_VERIFY | Skip TLS verification for WALRUS API. Use when testing with self-signed certificates. Valid when Walrus toolkit is enabled. | True |
| WALRUS_DEFAULT_PROJECT | Project name for the default context, valid when Walrus toolkit is enabled. | "" |
| WALRUS_DEFAULT_ENVIRONMENT | Environment name for the default context, valid when Walrus toolkit is enabled. | "" |

### Using Walrus Backend

Walrus backend provides features like hybrid infrastructure support, environment management, etc.
To enable Walrus backend, edit the envfile:

1. Set `TOOLKITS=walrus`
2. Fill in `OPENAI_API_KEY`, `WALRUS_URL` and `WALRUS_API_KEY`

Then you can run Appilot to get started:

```
make run
```

### Run with Docker

You can run Appilot in docker container when using Walrus backend.

> **Prerequisites:** Install `docker`.

1. Get an envfile by running the following command.

```
mv .env.example .env
```

2. Configure the `.env` file.

- Set `TOOLKITS=walrus`
- Fill in `OPENAI_API_KEY`, `WALRUS_URL` and `WALRUS_API_KEY`

3. Run the following command:

```
docker run -it --env-file .env sealio/appilot:main
```

## How it works

The following is the architecture diagram of Appilot:

![appilot-arch](https://github.com/seal-io/appilot/assets/5697937/914cb60d-60ab-4b4d-8661-82f89d85683b)

## License

Copyright (c) 2023 [Seal, Inc.](https://seal.io)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [LICENSE](./LICENSE) file for details.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
