from typing import Any
from langchain.agents.tools import BaseTool
from callbacks.approval import ApprovalCallbackHandler

class RequireApprovalTool(BaseTool):
    """Tool that requires human approval."""
    def __init__(self, **data: Any) -> None:
        super().__init__(
            callbacks=[ApprovalCallbackHandler()], **data
        )
