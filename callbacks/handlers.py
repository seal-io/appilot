from typing import Any, Dict, Optional, List, Union
from uuid import UUID

from i18n import text
from utils import utils
from config import config

from langchain.callbacks.base import BaseCallbackHandler,LLMManagerMixin
from langchain.schema.output import LLMResult
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.schema.output import LLMResult

class HumanRejectedException(Exception):
    """Exception to raise when a person manually review and rejects a value."""


class ApprovalCallbackHandler(BaseCallbackHandler):
    """Callback for manual approval."""

    raise_error: bool = True

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if not self._approve(input_str,serialized):
            raise HumanRejectedException(
                f"Inputs {input_str} to tool {serialized} were rejected."
            )

    def _approve(self, _input: str, serialized: Dict[str, Any]) -> bool:
        message = text.get("ask_approval")
        resp = input(message.format(input=_input, tool_name=serialized["name"]))
        return resp.lower() in ("yes", "y")
    

class PrintReasoningCallbackHandler(BaseCallbackHandler):
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        if not config.CONFIG.show_reasoning:
            return 
        
        generation_text = response.generations[0][0].text
        lines = generation_text.splitlines()
        reason_prompt_prefix = "Reason:"
        for line in reversed(lines):
            if line.startswith(reason_prompt_prefix):
                reason_text = line.lstrip("Reason:").strip()
                utils.print_ai_reasoning(reason_text)
                break
        """Print AI reasoning."""
    

class DebugCallbackHandler(BaseCallbackHandler, LLMManagerMixin):

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_llm_end")
        """Run when LLM ends running."""
    
    def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_llm_new_token")
        """Run on new LLM token. Only available when streaming is enabled."""


    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_llm_error")
        """Run when LLM errors."""

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_chain_start")
        """Run when chain starts running."""

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_chain_end")
        """Run when chain ends running."""

    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_chain_error")
        """Run when chain errors."""

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_tool_start")
        """Run when tool starts running."""

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_tool_end")
        """Run when tool ends running."""

    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_tool_error")
        """Run when tool errors."""

    def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_text")
        """Run on arbitrary text."""

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_agent_action")
        """Run on agent action."""

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        print("on_agent_finish")
        """Run on agent end."""
