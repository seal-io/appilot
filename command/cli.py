from typing import Any
import readline

from callbacks import handlers
from config import config
from i18n import text
from walrus.client import WalrusClient
from utils import utils
from agent.agent import create_agent

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import colorama

last_error = None


def setup_agent() -> Any:
    config.init()
    colorama.init()

    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0.0,
        callbacks=[handlers.PrintReasoningCallbackHandler()],
    )

    text.init_system_messages(llm)

    walrus_client = WalrusClient(
        config.CONFIG.walrus_url,
        config.CONFIG.walrus_api_key,
        verify=(not config.CONFIG.skip_tls_verify),
    )

    memory = ConversationBufferMemory(memory_key="chat_history")

    return create_agent(
        walrus_client, llm, shared_memory=memory, verbose=config.CONFIG.verbose
    )


def run():
    appilot_agent = setup_agent()

    print(text.get("welcome"))
    user_query = None
    while True:
        user_query = input(">")
        if not user_query.strip():
            continue
        elif user_query == "exit":
            break
        elif user_query == "appilot_log":
            print_last_error()
            continue

        try:
            result = appilot_agent.run(user_query)
        except handlers.HumanRejectedException as he:
            utils.print_rejected_message()
            continue
        except Exception as e:
            handle_exception(e)
            continue

        utils.print_ai_response(result)


def handle_exception(e):
    global last_error
    print(text.get("response_prefix"), end="")
    print(text.get("error_occur_message"))
    last_error = e


def print_last_error():
    if last_error is None:
        print(text.get("response_prefix"), end="")
        print(text.get("no_error_message"))
    else:
        print(last_error)
