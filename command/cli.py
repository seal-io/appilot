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
        result = appilot_agent.run(user_query)
        utils.print_ai_response(result)
