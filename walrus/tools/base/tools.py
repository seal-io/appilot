from typing import Any
from langchain.agents.tools import BaseTool
from walrus.client import WalrusClient


class WalrusTool(BaseTool):
    """Tool to interacte with Walrus APIs."""

    walrus_client: WalrusClient
