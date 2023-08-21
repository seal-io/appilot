from typing import Any
from langchain.agents.tools import BaseTool
from callbacks.handlers import ApprovalCallbackHandler, DebugCallbackHandler
from walrus.client import WalrusClient


class RequireApprovalTool(BaseTool):
    """Tool that requires human approval."""

    def __init__(self, **data: Any) -> None:
        super().__init__(callbacks=[ApprovalCallbackHandler()], **data)


class DebugHandlerTool(BaseTool):

    """Tool that requires human approval."""

    def __init__(self, **data: Any) -> None:
        super().__init__(callbacks=[DebugCallbackHandler()], **data)


class WalrusTool(BaseTool):
    """Tool to interacte with Walrus APIs."""

    walrus_client: WalrusClient
