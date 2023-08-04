# Appilot

Appilot`[ə'paɪlət]` stands for application-pilot.
It is an experimental project that introduces GPTOps: operate your applications using GPT-like LLM.

## Demo

```
!!!TODO!!!
- deploy nginx.
- use helm to deploy an ELK stack.
- deploy a llama2 instance on AWS.
- upgrade and clean up a service.
- clone an environment.
- diagnose and resolve a service NotReady issue.
```

## Feature

- Application management: deploy, upgrade, rollback, etc.
- Environment management: clone, view topology, etc.
- Diagnose: find flaws and ask AI to fix.
- Other operations: view logs, access terminal to debug, etc.
- Safeguard: any action involving state changes requires human approval.
- Hybrid infrastructure: works on kubernetes, VM, cloud, on-prem.
- Multi language support: It's not limited to English. Operate with the natural language you prefer.

## Run

**prerequistes:**

- Get OpenAI API key with access to the gpt-4 model.
- Install [Seal](https://github.com/seal-io/seal) and get the url and API key. Seal is an open source software that can be run by a docker run command. It serves as the engine for application management.

### Run with Docker

**Prerequisites:** `docker` installed.

1. Fill in envfile by running:

```
mv .env.example .env
```

then set variables in `.env` file

2. Run the following command:

```
docker run -it --env-file .env appilot
```

### Run locally in python virtual environment

**Prerequisites:** `python3` and `make` installed.

1. Fill in envfile by running

```
mv .env.example .env
```

then set variables in `.env` file

2. Run the following command to install. It will create a venv and install required dependencies.

```
make install
```

3. Run Appilot:

```
make run
```
