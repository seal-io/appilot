from langchain.agents.tools import BaseTool
from seal.client import SealClient


class GetTemplateSchemaTool(BaseTool):
    """Tool to get template version and schema given template id."""

    name = "get_template_schema"
    description = (
        "Get template version and schema given template id."
        "Input should be a template id."
        "Output template schema."
    )
    seal_client: SealClient

    def _run(self, query: str) -> str:
        return self.seal_client.get_template_version(query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
