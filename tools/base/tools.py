from typing import Any
from langchain.agents.tools import BaseTool
from callbacks.handlers import ApprovalCallbackHandler, DebugCallbackHandler


class RequireApprovalTool(BaseTool):
    """Tool that requires human approval."""

    def __init__(self, **data: Any) -> None:
        super().__init__(callbacks=[ApprovalCallbackHandler()], **data)


class DebugHandlerTool(BaseTool):

    """Tool that requires human approval."""

    def __init__(self, **data: Any) -> None:
        super().__init__(callbacks=[DebugCallbackHandler()], **data)
