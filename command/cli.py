import sys
from typing import Any
import readline


from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import colorama

from callbacks import handlers
from config import config
from i18n import text
from utils import utils
from agent.agent import create_agent
from walrus.toolkit import WalrusToolKit
from k8s.toolkit import KubernetesToolKit

last_error = None


def setup_agent() -> Any:
    config.init()
    colorama.init()

    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0,
        callbacks=[handlers.PrintReasoningCallbackHandler()],
    )

    text.init_system_messages(llm)

    memory = ConversationBufferMemory(memory_key="chat_history")

    tools = []
    if "kubernetes" in config.APPILOT_CONFIG.toolkits:
        kubernetes_toolkit = KubernetesToolKit(llm=llm)
        tools.extend(kubernetes_toolkit.get_tools())
    elif "walrus" in config.APPILOT_CONFIG.toolkits:
        walrus_toolkit = WalrusToolKit(llm=llm)
        tools.extend(walrus_toolkit.get_tools())
    else:
        print(text.get("enable_no_toolkit"))
        sys.exit(1)

    return create_agent(
        llm,
        shared_memory=memory,
        tools=tools,
        verbose=config.APPILOT_CONFIG.verbose,
    )


def run():
    appilot_agent = setup_agent()

    print(text.get("welcome"))
    user_query = None
    while True:
        user_query = input(">")
        if utils.is_inform_sent():
            continue
        elif user_query == "exit":
            break
        elif user_query == "appilot_log":
            print_last_error()
            continue
        elif user_query.startswith("#"):
            continue
        elif not user_query.strip():
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
