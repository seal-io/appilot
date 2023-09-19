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

Deploying llama-2 on AWS:

https://github.com/seal-io/appilot/assets/5697937/0562fe29-8e97-42ba-bbf6-eaa5b5fefc41

Other use cases:

- [Manage applications in Kubernetes using helm charts](./examples/k8s_helm.md)
- [Operating native Kubernetes resources](./examples/k8s_yaml.md)

## Run

**prerequistes:**

- Get OpenAI API key with access to the gpt-4 model.
- For [Walrus](https://github.com/seal-io/walrus) backend
  - Install Walrus and get the url and API key. Walrus is an open source software that can be run by a docker command. It serves as the engine for application management.
- For [Kubernetes](https://kubernetes.io) backend
  - Install [kubectl](https://kubernetes.io/docs/tasks/tools/) and [helm](https://helm.sh/docs/intro/install/)
  - Have a running Kubernetes cluster

### Run locally in python virtual environment

**Prerequisites:** `python3` and `make` installed.

1. Get an envfile by running the following command.

```
mv .env.example .env
```

2. Configure the `.env` file.

For Walrus backend,

- Set `TOOLKITS=walrus`
- Fill in `OPENAI_API_KEY`, `WALRUS_URL` and `WALRUS_API_KEY`

For Kubernetes backend,

- Set `TOOLKITS=kubernetes`
- Fill in `OPENAI_API_KEY`

3. Run the following command to install. It will create a venv and install required dependencies.

```
make install
```

3. Run the following command:

```
make run
```

### Run with Docker

**Prerequisites:** `docker` installed.

1. Get an envfile by running the following command.

```
mv .env.example .env
```

2. Configure the `.env` file.

For Walrus backend,

- Set `TOOLKITS=walrus`
- Fill in `OPENAI_API_KEY`, `WALRUS_URL` and `WALRUS_API_KEY`

For Kubernetes backend,

- Set `TOOLKITS=kubernetes`
- Fill in `OPENAI_API_KEY`

3. Run the following command:

```
docker run -it --env-file .env sealio/appilot:main
```
