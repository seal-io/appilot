from langchain.schema.language_model import BaseLanguageModel
from kubernetes import config

from k8s import context
from k8s.tools.helm.tool import (
    DeleteApplicationTool,
    DeployApplicationTool,
    GetApplicationAccessEndpointsTool,
    GetApplicationDetailTool,
    ListApplicationsTool,
    SearchChartTool,
)
from k8s.tools.manage_resource.tool import (
    ApplyResourcesTool,
    ConstructResourceTool,
    DeleteResourceTool,
    GetPodLogsTool,
    GetResourceDetailTool,
    ListResourcesTool,
    WatchResourcesTool,
)
from walrus.tools.general.tools import BrowseURLTool


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
            ListResourcesTool(return_direct=True),
            GetResourceDetailTool(),
            GetPodLogsTool(return_direct=True),
            WatchResourcesTool(return_direct=True),
            DeleteResourceTool(),
            ConstructResourceTool(llm=llm),
            ApplyResourcesTool(),
            SearchChartTool(llm=llm),
            DeployApplicationTool(),
            ListApplicationsTool(),
            GetApplicationDetailTool(),
            GetApplicationAccessEndpointsTool(),
            BrowseURLTool(),
            DeleteApplicationTool(),
        ]
        return tools
