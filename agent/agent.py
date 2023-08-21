from typing import Any, Dict, Optional

from config import config
from walrus.client import WalrusClient
from tools.reasoning.tool import ShowReasoningTool, HideReasoningTool
from agent.prompt import (
    AGENT_PROMPT_PREFIX,
    FORMAT_INSTRUCTIONS_TEMPLATE,
)
from tools.manage_service.tool import (
    ConstructServiceToCreateTool,
    ConstructServiceToUpdateTool,
    GetServicesTool,
    CreateServiceTool,
    DeleteServicesTool,
    GetServiceAccessEndpointsTool,
    ListServicesTool,
    UpdateServiceTool,
    ListServiceResourcesTool,
    GetServiceResourceKeysTool,
    GetServiceResourceLogsTool,
    GetServiceDependencyGraphTool,
)
from tools.manage_context.tool import ChangeContextTool, CurrentContextTool
from tools.manage_environment.tool import (
    ListEnvironmentsTool,
    DeleteEnvironmentsTool,
    GetEnvironmentDependencyGraphTool,
)
from tools.manage_project.tool import ListProjectsTool
from tools.manage_template.tool import MatchTemplateTool, GetTemplateSchemaTool
from tools.human.tool import HumanTool

from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.memory import ReadOnlySharedMemory
from langchain.schema.language_model import BaseLanguageModel


def create_agent(
    walrus_client: WalrusClient,
    llm: BaseLanguageModel,
    shared_memory: Optional[ReadOnlySharedMemory] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    verbose: bool = True,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Instantiate planner for a given task."""

    tools = [
        HumanTool(),
        ShowReasoningTool(),
        HideReasoningTool(),
        CurrentContextTool(),
        ChangeContextTool(walrus_client=walrus_client),
        ListProjectsTool(walrus_client=walrus_client),
        ListEnvironmentsTool(walrus_client=walrus_client),
        DeleteEnvironmentsTool(walrus_client=walrus_client),
        GetEnvironmentDependencyGraphTool(walrus_client=walrus_client),
        MatchTemplateTool(llm=llm, walrus_client=walrus_client),
        GetTemplateSchemaTool(walrus_client=walrus_client),
        ConstructServiceToCreateTool(llm=llm, walrus_client=walrus_client),
        ConstructServiceToUpdateTool(llm=llm, walrus_client=walrus_client),
        GetServicesTool(walrus_client=walrus_client),
        ListServicesTool(walrus_client=walrus_client),
        CreateServiceTool(walrus_client=walrus_client),
        UpdateServiceTool(walrus_client=walrus_client),
        DeleteServicesTool(walrus_client=walrus_client),
        ListServiceResourcesTool(walrus_client=walrus_client),
        GetServiceResourceKeysTool(walrus_client=walrus_client),
        GetServiceResourceLogsTool(walrus_client=walrus_client),
        GetServiceAccessEndpointsTool(walrus_client=walrus_client),
        GetServiceDependencyGraphTool(walrus_client=walrus_client),
    ]

    format_instructions = FORMAT_INSTRUCTIONS_TEMPLATE.format(
        natural_language=config.CONFIG.natural_language
    )
    prompt = ConversationalAgent.create_prompt(
        tools,
        prefix=AGENT_PROMPT_PREFIX,
        format_instructions=format_instructions,
    )

    agent = ConversationalAgent(
        llm_chain=LLMChain(
            llm=llm, prompt=prompt, verbose=config.CONFIG.verbose
        ),
        allowed_tools=[tool.name for tool in tools],
        **kwargs,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=shared_memory,
        callback_manager=callback_manager,
        verbose=verbose,
        **(agent_executor_kwargs or {}),
    )
