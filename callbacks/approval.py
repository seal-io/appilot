from typing import Any, Dict, Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler

from i18n import text

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