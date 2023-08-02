# appilot
Appilot`[ə'paɪlət]` stands for application-pilot.
It's an experimental project that introduces GPTOps: operate your applications using GPT-like LLM.

## Demo

```
TODO
```

## Feature
- Application management: deploy, upgrade, rollback, etc.
- Environment management: clone, view topology, etc.
- Hybrid infrastructure: works on kubernetes, VM, cloud, on-prem.
- Diagnose: find flaws and ask AI to fix.
- Safeguard: any action involving state changes requires human approval.
- Other operations: view logs, access terminal to debug, etc.

## Run

**prerequistes:**
1. Get openai API key with access to the gpt-4 model.
2. Install [Seal](https://github.com/seal-io/seal) and get the url and API key. Seal is an open source software that can be run by a docker run command. It serves as the engine for application management.

### Run with Docker

**Prerequisite:** docker installed.

```
docker run -it \
-e OPENAI_API_KEY=${OPENAI_API_KEY} \
-e SEAL_URL=${SEAL_URL} \
-e SEAL_API_KEY=${SEAL_API_KEY} \
-e VERBOSE=${VERBOSE} \
appilot
```

### Run without Docker

**Prerequisite:** python3 installed.

1. Prepare venv
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set envvars
```
export OPENAI_API_KEY=<your-key>
export SEAL_URL=<your-url>
export SEAL_API_KEY=<your-key>
export VERBOSE=1
```

3. Run
```
python app.py
```