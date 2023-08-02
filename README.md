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
- Multi language support: It's not limited to English. Operate with the natural language you prefer.

## Run

**prerequistes:**
1. Get openai API key with access to the gpt-4 model.
2. Install [Seal](https://github.com/seal-io/seal) and get the url and API key. Seal is an open source software that can be run by a docker run command. It serves as the engine for application management.

### Run with Docker

**Prerequisite:** docker installed.

1. Run
```
mv .env.example .env
```
2. Fill in the `.env` file
3. Run
```
docker run -it --env-file .env appilot
```

### Run without Docker

**Prerequisite:** python3 installed.

1. Prepare venv
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Run
```
mv .env.example .env
```
3. Fill in the `.env` file
4. Run
```
python app.py
```