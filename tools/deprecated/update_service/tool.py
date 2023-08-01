import json
from typing import Any
from langchain.agents.tools import BaseTool
from callbacks.approval import ApprovalCallbackHandler
from config import config
from seal.client import SealClient


class UpdateServiceTool(BaseTool):
    """Tool to update a service."""

    name = "update_service"
    description = (
        "Update a service."
        "Input should be a service object in json format."
        'Output a json string with 2 keys, "id" and "name" of the service.'
    )
    seal_client: SealClient

    def __init__(self, **data: Any) -> None:
        super().__init__(
            callbacks=[ApprovalCallbackHandler(tool_name="update_service")], **data
        )

    def _run(self, text: str) -> str:
        project_id = config.Config.context.project_id
        environment_id = config.Config.context.environment_id
        return self.seal_client.update_service(project_id, environment_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")
