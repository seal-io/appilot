from typing import Any, Dict, Optional

from config import config
from walrus.toolkit import WalrusToolKit
from tools.reasoning.tool import ShowReasoningTool, HideReasoningTool
from agent.prompt import (
    AGENT_PROMPT_PREFIX,
    FORMAT_INSTRUCTIONS_TEMPLATE,
)
from tools.human.tool import HumanTool

from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.memory import ReadOnlySharedMemory
from langchain.schema.language_model import BaseLanguageModel


def create_agent(
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
    ]

    walrus_toolkit = WalrusToolKit(llm=llm)
    tools.extend(walrus_toolkit.get_tools())

    format_instructions = FORMAT_INSTRUCTIONS_TEMPLATE.format(
        natural_language=config.APPILOT_CONFIG.natural_language
    )
    prompt = ConversationalAgent.create_prompt(
        tools,
        prefix=AGENT_PROMPT_PREFIX,
        format_instructions=format_instructions,
    )

    agent = ConversationalAgent(
        llm_chain=LLMChain(
            llm=llm, prompt=prompt, verbose=config.APPILOT_CONFIG.verbose
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
