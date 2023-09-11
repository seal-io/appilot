from typing import Any
from langchain.agents.tools import BaseTool
from kubernetes import client


class KubernetesTool(BaseTool):
    """Tool to interacte with Walrus APIs."""

    client: client
