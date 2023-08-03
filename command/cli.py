
from typing import Any

from callbacks import handlers
from config import config
from i18n import text
from seal.client import SealClient
from utils import utils
from agent.agent import create_seal_agent

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import colorama

def setup_agent() -> Any:
    config.initConfig()
    colorama.init()

    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0.0,
        callbacks=[handlers.PrintReasoningCallbackHandler()],
    )

    text.init_system_messages(llm)

    seal_client = SealClient(
        config.CONFIG.seal_url,
        config.CONFIG.seal_api_key,
        verify=False,
    )

    memory = ConversationBufferMemory(memory_key="chat_history")

    return create_seal_agent(
        seal_client, llm, shared_memory=memory, verbose=utils.verbose()
    )

def run():
    seal_agent = setup_agent()

    print(text.get("welcome"))
    user_query = None
    while user_query != "exit":
        user_query = input(">")
        if not user_query.strip():
            continue
        result = seal_agent.run(user_query)
        utils.print_ai_response(result)
