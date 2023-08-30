import json

from config import config

from langchain.schema.language_model import BaseLanguageModel

prompt = """
Translate the following json map to {language}. Keep the keys unchanged.
{messages}

RESULT:

"""

system_messages = {
    "welcome": "Appilot: What can I help?",
    "ai_reasoning": "Appilot reasoning:",
    "response_prefix": "Appilot: ",
    "inform_prefix": "Appilot[inform]: ",
    "error_occur_message": "An internal error occurred. Enter 'appilot_log' if you want to see the details.",
    "rejected_message": "The action is rejected.",
    "no_error_message": "No error occurred.",
    "resource_log_prefix": "Here's the log:",
    "watch_service_note": "( Enter <Ctrl + C> to halt )",
    "watch_service_ending": "Halted.",
    "show_graph_message": "The dependency graph is shown to you.",
    "inform_ready_start": "Start watching. Will inform when it's ready.",
    "service_ready_message": "Service {} is Ready.",
    "ask_approval": """
The following action requires approval:

Input:
{input}

Action: 
{tool_name}
 
Do you approve the above action? """,
}


def init_system_messages(llm: BaseLanguageModel):
    language = config.CONFIG.natural_language
    if language.lower() in ("en", "english"):
        return

    global system_messages
    system_messages_string = json.dumps(system_messages, ensure_ascii=False)
    result = llm.predict(
        prompt.format(language=language, messages=system_messages_string)
    )
    translated = json.loads(result)
    system_messages = translated


def get(key):
    return system_messages[key]
