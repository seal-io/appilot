from typing import Callable

from langchain.tools.base import BaseTool


class SealDeployRun(BaseTool):
    """Tool that Deploys a Seal service."""

    name = "Seal Deploy"
    description = (
        "Deploy a service to an environment in Seal system."
        "Useful for deploying applications, provisionging infrastructure."
        "Input should be a deployment task."
    )
    prompt_func: Callable[[str], None]
    input_func: Callable

    def _run(self, query: str) -> str:
        """Use the Seal deploy tool."""
        self.prompt_func(query)
        return self.input_func()

    async def _arun(self, query: str) -> str:
        """Use the Seal deploy tool asynchronously."""
        raise NotImplementedError("async not yet supported")
