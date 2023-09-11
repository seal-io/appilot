from langchain.schema.language_model import BaseLanguageModel
from kubernetes import config

from k8s import context
from k8s.tools.manage_resource.tool import (
    ApplyResourcesTool,
    ConstructResourceTool,
    DeleteResourceTool,
    GetResourceDetailTool,
    ListResourcesTool,
)


class KubernetesToolKit:
    """Kubernetes toolkit."""

    llm: BaseLanguageModel

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        config.load_kube_config()
        context.init_api_resources_cache()

    def get_tools(self):
        llm = self.llm
        tools = [
            ListResourcesTool(),
            GetResourceDetailTool(),
            DeleteResourceTool(),
            ConstructResourceTool(llm=llm),
            ApplyResourcesTool(),
        ]
        return tools
