from typing import Any, Dict, Optional

from config import config
from seal.client import SealClient
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


def create_seal_agent(
    seal_client: SealClient,
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
        ChangeContextTool(seal_client=seal_client),
        ListProjectsTool(seal_client=seal_client),
        ListEnvironmentsTool(seal_client=seal_client),
        DeleteEnvironmentsTool(seal_client=seal_client),
        GetEnvironmentDependencyGraphTool(seal_client=seal_client),
        MatchTemplateTool(llm=llm, seal_client=seal_client),
        GetTemplateSchemaTool(seal_client=seal_client),
        ConstructServiceToCreateTool(llm=llm, seal_client=seal_client),
        ConstructServiceToUpdateTool(llm=llm, seal_client=seal_client),
        GetServicesTool(seal_client=seal_client),
        ListServicesTool(seal_client=seal_client),
        CreateServiceTool(seal_client=seal_client),
        UpdateServiceTool(seal_client=seal_client),
        DeleteServicesTool(seal_client=seal_client),
        ListServiceResourcesTool(seal_client=seal_client),
        GetServiceResourceKeysTool(seal_client=seal_client),
        GetServiceResourceLogsTool(seal_client=seal_client),
        GetServiceAccessEndpointsTool(seal_client=seal_client),
        GetServiceDependencyGraphTool(seal_client=seal_client),
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
