import json
from typing import Any
from config import config
from walrus.client import WalrusClient
from langchain.agents.tools import BaseTool
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from tools.base.tools import RequireApprovalTool
from tools.manage_service.prompt import (
    CONSTRUCT_SERVICE_TO_CREATE_PROMPT,
    CONSTRUCT_SERVICE_TO_UPDATE_PROMPT,
)


class ListServicesTool(BaseTool):
    """Tool to list services."""

    name = "list_services"
    description = "List services."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        services = self.walrus_client.list_services(project_id, environment_id)
        return json.dumps(services)


class GetServicesTool(BaseTool):
    """Tool to get a service."""

    name = "get_service"
    description = "Get a service object. Input should be a service name."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        service = self.walrus_client.get_service_by_name(
            project_id, environment_id, query
        )
        return json.dumps(service)


class CreateServiceTool(RequireApprovalTool):
    """Tool to create a service."""

    name = "create_service"
    description = (
        "Create a service."
        "Input should be a service object in json format."
        'Output a json string with 2 keys, "id" and "name" of the service.'
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            # verify input
            json.loads(text)
        except json.JSONDecodeError as e:
            raise e

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        return self.walrus_client.create_service(
            project_id, environment_id, text
        )


class UpdateServiceTool(RequireApprovalTool):
    """Tool to update a service."""

    name = "update_service"
    description = (
        "Update a service."
        "Input should be a service object in json format."
        'Output a json string with 2 keys, "id" and "name" of the service.'
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        return self.walrus_client.update_service(
            project_id, environment_id, text
        )


class DeleteServicesTool(RequireApprovalTool):
    """Tool to delete one or multiple services."""

    name = "delete_services"
    description = (
        "Delete one or multiple services. Input should be ids of services."
    )
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.walrus_client.delete_services(project_id, query)


class GetServiceAccessEndpointsTool(BaseTool):
    """Tool to get access endpoints of a service."""

    name = "get_service_access_endpoints"
    description = (
        "Get access endpoints of a service."
        "Input should be id of a service."
        "Output service access endpoints."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.walrus_client.get_service_access_endpoints(
            project_id, text
        )


class ListServiceResourcesTool(BaseTool):
    """Tool to get resources of a service."""

    name = "get_service_resources"
    description = (
        "Get resources of a service. "
        "Helpful to know what resources a service consists of, what status they are in. "
        "Input should be id of a service. "
        "Output resource objects in json format."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.walrus_client.list_service_resources(project_id, text)


class GetServiceDependencyGraphTool(BaseTool):
    """Tool to get service dependency graph."""

    name = "get_service_dependency_graph"
    description = (
        "Get dependency graph of a service. Input should be a service id."
        "Output is a json data wrapped in triple backticks, representing the dependency graph."
        "You can directly return the output to the user. No need to reformat. "
        "UI can use this data to render the graph."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        data = {
            "project_id": config.CONFIG.context.project_id,
            "service_id": text,
        }
        return f"```service_resource_graph\n{data}\n```"


class GetServiceResourceKeysTool(BaseTool):
    """Tool to get keys of a service resource."""

    name = "get_service_resource_keys"
    description = (
        "Get keys of a service resource. "
        "Key is identity of a service resource's component. It is needed when you need logs or terminal access of a resource. "
        "Input is id of a service resource."
        "Output is keys in json format."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.walrus_client.get_service_resource_keys(project_id, text)


class GetServiceResourceLogsTool(BaseTool):
    """Tool to get logs of a service resource."""

    name = "get_service_resource_logs"
    description = (
        "Get logs of a service resource. "
        "Before using this tool, you should get keys of the resource first."
        'Input should be a json with 2 keys: "service_resource_id", "key".'
        '"key" is identity of a service resource\'s component. It is required when you need logs or terminal access of a resource. '
        "Output is log text."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            input = json.loads(text)
        except json.JSONDecodeError as e:
            raise e
        service_resource_id = input["service_resource_id"]
        key = input["key"]

        project_id = config.CONFIG.context.project_id
        return self.walrus_client.get_service_resource_logs(
            project_id, service_resource_id, key
        )


class ConstructServiceToCreateTool(BaseTool):
    """Construct a service for deployment in Walrus system."""

    name = "construct_service_to_create"
    description = (
        "Construct a service for creation in Walrus system."
        'Input to the tool should be a json with 3 keys: "user_query" and "related_template_id".'
        'The value of "user_query" should be the description of a deployment task.'
        'The value of "related_template_id" should be id of a template related to the deployment task.'
        "The output is a service object in json. It will be used in the creation of a service."
    )
    llm: BaseLanguageModel
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise e

        query = data.get("user_query")
        template_id = data.get("related_template_id")

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        existing_services = self.walrus_client.list_services(
            project_id, environment_id
        )
        related_template = self.walrus_client.get_template_version(template_id)

        prompt = PromptTemplate(
            template=CONSTRUCT_SERVICE_TO_CREATE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "context": json.dumps(config.CONFIG.context.__dict__),
                "existing_services": json.dumps(existing_services),
                "related_template": json.dumps(related_template),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(json.dumps(query)).strip()


class ConstructServiceToUpdateTool(BaseTool):
    """Construct a service for upgrade in Walrus system."""

    name = "construct_service_to_update"
    description = (
        "Construct a service for update in Walrus system."
        'Input to the tool should be a json with 3 keys: "user_query", "service_name" and "related_template_id".'
        'The value of "user_query" should be the description of a deployment task.'
        'The value of "service_name" should be name of the service about to update.'
        'The value of "related_template_id" should be id of a template related to the deployment task.'
        "The output is a service object in json. It will be used in the update of a service."
    )
    llm: BaseLanguageModel
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise e

        query = data.get("user_query")
        service_name = data.get("service_name")
        template_id = data.get("related_template_id")

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        related_template = self.walrus_client.get_template_version(template_id)
        current_service = self.walrus_client.get_service_by_name(
            project_id=project_id,
            environment_id=environment_id,
            service_name=service_name,
        )

        prompt = PromptTemplate(
            template=CONSTRUCT_SERVICE_TO_UPDATE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "context": json.dumps(config.CONFIG.context.__dict__),
                "current_service": json.dumps(current_service),
                "related_template": json.dumps(related_template),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(json.dumps(query)).strip()
