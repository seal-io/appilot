import urllib3
from walrus import context
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
from utils import utils


class WalrusToolKit:
    """Walrus toolkit."""

    walrus_client: WalrusClient
    llm: BaseLanguageModel

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.init_client()

    def init_client(self):
        walrus_api_key = utils.get_env("WALRUS_API_KEY")
        walrus_url = utils.get_env("WALRUS_URL")
        walrus_default_project = utils.get_env("WALRUS_DEFAULT_PROJECT")
        walrus_default_environment = utils.get_env(
            "WALRUS_DEFAULT_ENVIRONMENT"
        )
        walrus_skip_tls_verify = utils.get_env_bool(
            "WALRUS_SKIP_TLS_VERIFY", False
        )
        if walrus_skip_tls_verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if not walrus_url:
            raise Exception("WALRUS_URL is not set")
        if not walrus_api_key:
            raise Exception("WALRUS_API_KEY is not set")

        self.walrus_client = WalrusClient(
            walrus_url,
            walrus_api_key,
            verify=(not walrus_skip_tls_verify),
        )
        context.set_default(
            walrus_url=walrus_url,
            walrus_api_key=walrus_api_key,
            default_project=walrus_default_project,
            default_environment=walrus_default_environment,
        )

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
