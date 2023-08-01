import json
from typing import Any
from langchain.agents.tools import BaseTool
from callbacks.approval import ApprovalCallbackHandler
from config import config
from seal.client import SealClient


class GetServiceAccessEndpointsTool(BaseTool):
    """Tool to get access endpoints of a service."""

    name = "get_service_access_endpoints"
    description = (
        "Get access endpoints of a service."
        "Input should be id of a service."
        "Output service access endpoints."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        project_id = config.Config.context.project_id
        return self.seal_client.get_service_access_endpoints(project_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")
