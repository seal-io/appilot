import logging
import subprocess
import sys
from langchain.schema.language_model import BaseLanguageModel
from kubernetes import config, client

from k8s import context
from k8s.tools.helm.tool import (
    DeleteApplicationTool,
    DeployApplicationTool,
    GenerateUpgradeApplicationValuesTool,
    GetApplicationAccessEndpointsTool,
    GetApplicationDetailTool,
    ListApplicationsTool,
    SearchChartTool,
    UpgradeApplicationTool,
)
from k8s.tools.manage_resource.tool import (
    ApplyResourcesTool,
    ConstructResourceForUpdateTool,
    ConstructResourceTool,
    DeleteResourceTool,
    DescribePodTool,
    GetIngressAccessEndpointsTool,
    GetPodLogsTool,
    GetResourceDetailTool,
    GetResourceYamlTool,
    GetServiceAccessEndpointsTool,
    ListResourcesForInfoTool,
    ListResourcesTool,
    WatchResourcesTool,
)
from walrus.tools.general.tools import BrowseURLTool

logger = logging.getLogger(__name__)


def command_installed(commands: list[str]):
    try:
        result = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


class KubernetesToolKit:
    """Kubernetes toolkit."""

    llm: BaseLanguageModel

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        config.load_kube_config()
        self.precheck()
        context.init_api_resources_cache()

    def precheck(self):
        if not command_installed(["kubectl", "version", "--client"]):
            print("Precheck failed: kubectl not found.")
            sys.exit(1)

        if not command_installed(["helm", "version"]):
            print("Precheck failed: helm not found.")
            sys.exit(1)

        try:
            client.VersionApi().get_code(_request_timeout=2)
        except Exception as e:
            logger.debug("Error connecting to Kubernetes cluster: {e}")
            print("Precheck failed: Kubernetes cluster is not available.")
            sys.exit(1)

    def get_tools(self):
        llm = self.llm
        tools = [
            ListResourcesTool(return_direct=True),
            ListResourcesForInfoTool(),
            GetResourceDetailTool(),
            GetResourceYamlTool(return_direct=True),
            GetServiceAccessEndpointsTool(),
            GetIngressAccessEndpointsTool(),
            GetPodLogsTool(),
            DescribePodTool(),
            WatchResourcesTool(return_direct=True),
            DeleteResourceTool(),
            ConstructResourceTool(llm=llm),
            ConstructResourceForUpdateTool(llm=llm),
            ApplyResourcesTool(),
            SearchChartTool(llm=llm),
            DeployApplicationTool(),
            GenerateUpgradeApplicationValuesTool(llm=llm),
            UpgradeApplicationTool(),
            ListApplicationsTool(),
            GetApplicationDetailTool(),
            GetApplicationAccessEndpointsTool(),
            BrowseURLTool(),
            DeleteApplicationTool(),
        ]
        return tools
