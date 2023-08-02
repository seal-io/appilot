from langchain.chat_models import ChatOpenAI
from config import config
from config.config import initConfig
from i18n import text
from seal.client import SealClient
from utils import utils
from agent.agent import create_seal_agent
from langchain.memory import ConversationBufferMemory

initConfig()

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.0,
)

text.init_system_messages(llm)

seal_client = SealClient(
    config.CONFIG.seal_url,
    config.CONFIG.seal_api_key,
    verify=False,
)

memory = ConversationBufferMemory(memory_key="chat_history")
# memory = None
seal_agent = create_seal_agent(
    seal_client, llm, shared_memory=memory, verbose=utils.verbose()
)


# default_query = (
#     # "create a new project named 'hello'."
#     # "create an environment named 'dev' in project 'hello'."
#     # "clone a new environment named 'staging' from environment named 'dev'."
#     # "show me available environments"
#     # "What is the infrastrucre of available environment?"
#     # "Deploy nginx service named 'test2', use 256Mi memory"
#     "Update llama-2 service and use a larger VM instance"
# )

print(text.get("welcome"))
user_query = input(">")
while user_query != "exit":
    result = seal_agent.run(user_query)
    print(result)
    user_query = input(">")
