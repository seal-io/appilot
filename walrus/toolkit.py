from walrus.tools.general.tools import BrowseURLTool
from walrus.tools.manage_context.tool import (
    ChangeContextTool,
    CurrentContextTool,
)
from walrus.tools.manage_environment.tool import (
    CloneEnvironmentTool,
    DeleteEnvironmentsTool,
    GetEnvironmentDependencyGraphTool,
    ListEnvironmentsTool,
)
from walrus.tools.manage_project.tool import ListProjectsTool
from walrus.tools.manage_service.tool import (
    ConstructServiceToCreateTool,
    ConstructServiceToUpdateTool,
    CreateServiceTool,
    DeleteServicesTool,
    GetServiceAccessEndpointsTool,
    GetServiceDependencyGraphTool,
    GetServiceResourceLogsReturnDirectTool,
    GetServiceResourceLogsTool,
    GetServicesTool,
    InformServiceReadyTool,
    ListServiceResourcesTool,
    ListServicesInAllEnvironmentsTool,
    ListServicesTool,
    UpdateServiceTool,
    WatchServicesTool,
)
from walrus.tools.manage_template.tool import (
    GetTemplateSchemaTool,
    MatchTemplateTool,
)
from walrus.client import WalrusClient
from langchain.schema.language_model import BaseLanguageModel


class WalrusToolKit:
    """Walrus toolkit."""

    walrus_client: WalrusClient
    llm: BaseLanguageModel

    def __init__(self, llm: BaseLanguageModel, walrus_client: WalrusClient):
        self.llm = llm
        self.walrus_client = walrus_client

    def get_tools(self):
        walrus_client = self.walrus_client
        llm = self.llm
        tools = [
            CurrentContextTool(),
            ChangeContextTool(walrus_client=walrus_client),
            ListProjectsTool(walrus_client=walrus_client),
            ListEnvironmentsTool(walrus_client=walrus_client),
            DeleteEnvironmentsTool(walrus_client=walrus_client),
            CloneEnvironmentTool(walrus_client=walrus_client),
            GetEnvironmentDependencyGraphTool(
                walrus_client=walrus_client, return_direct=True
            ),
            MatchTemplateTool(llm=llm, walrus_client=walrus_client),
            GetTemplateSchemaTool(walrus_client=walrus_client),
            ConstructServiceToCreateTool(llm=llm, walrus_client=walrus_client),
            ConstructServiceToUpdateTool(llm=llm, walrus_client=walrus_client),
            GetServicesTool(walrus_client=walrus_client),
            ListServicesTool(walrus_client=walrus_client),
            WatchServicesTool(walrus_client=walrus_client, return_direct=True),
            InformServiceReadyTool(
                walrus_client=walrus_client, return_direct=True
            ),
            ListServicesInAllEnvironmentsTool(walrus_client=walrus_client),
            CreateServiceTool(walrus_client=walrus_client),
            UpdateServiceTool(walrus_client=walrus_client),
            DeleteServicesTool(walrus_client=walrus_client),
            ListServiceResourcesTool(walrus_client=walrus_client),
            GetServiceResourceLogsTool(walrus_client=walrus_client),
            GetServiceResourceLogsReturnDirectTool(
                walrus_client=walrus_client, return_direct=True
            ),
            GetServiceAccessEndpointsTool(walrus_client=walrus_client),
            BrowseURLTool(),
            GetServiceDependencyGraphTool(walrus_client=walrus_client),
        ]
        return tools
