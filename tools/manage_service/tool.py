import json
from typing import Any
from config import config
from seal.client import SealClient
from langchain.agents.tools import BaseTool
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from tools.base.tools import RequireApprovalTool
from tools.manage_service.prompt import (
    CONSTRUCT_SERVICE_PROMPT,
)


class ListServicesTool(BaseTool):
    """Tool to list services."""

    name = "list_services"
    description = "List services."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        services = self.seal_client.list_services(project_id, environment_id)
        return json.dumps(services)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class GetServicesTool(BaseTool):
    """Tool to get a service."""

    name = "get_service"
    description = "Get a service object. Input should be a service name."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        service = self.seal_client.get_service_by_name(
            project_id, environment_id, query
        )
        return json.dumps(service)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class CreateServiceTool(RequireApprovalTool):
    """Tool to create a service."""

    name = "create_service"
    description = (
        "Create a service."
        "Input should be a service object in json format."
        'Output a json string with 2 keys, "id" and "name" of the service.'
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        try:
            # verify input
            json.loads(text)
        except json.JSONDecodeError as e:
            raise e

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        return self.seal_client.create_service(project_id, environment_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


class UpdateServiceTool(RequireApprovalTool):
    """Tool to update a service."""

    name = "update_service"
    description = (
        "Update a service."
        "Input should be a service object in json format."
        'Output a json string with 2 keys, "id" and "name" of the service.'
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        return self.seal_client.update_service(project_id, environment_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class DeleteServicesTool(RequireApprovalTool):
    """Tool to delete one or multiple services."""

    name = "delete_services"
    description = "Delete one or multiple services. Input should be ids of services."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.seal_client.delete_services(project_id, query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class GetServiceAccessEndpointsTool(BaseTool):
    """Tool to get access endpoints of a service."""

    name = "get_service_access_endpoints"
    description = (
        "Get access endpoints of a service."
        "Input should be id of a service."
        "Output service access endpoints."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.seal_client.get_service_access_endpoints(project_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class ListServiceResourcesTool(BaseTool):
    """Tool to get resources of a service."""

    name = "get_service_resources"
    description = (
        "Get resources of a service. "
        "Helpful to know what resources a service consists of, what status they are in. "
        "Input should be id of a service in plain string. "
        "Output resource objects in json format."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.seal_client.list_service_resources(project_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class GetServiceDependencyGraphTool(BaseTool):
    """Tool to get service dependency graph."""

    name = "get_service_dependency_graph"
    description = (
        "Get dependency graph of a service. Input should be a service id."
        "Output is a json data wrapped in triple backticks, representing the dependency graph."
        "You can directly return the output to the user. No need to reformat. "
        "UI can use this data to render the graph."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        data = {
            "project_id": config.CONFIG.context.project_id,
            "service_id": text,
        }
        return f"```service_resource_graph\n{data}\n```"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class ConstructServiceTool(BaseTool):
    """Construct a service for deployment in Seal system."""

    name = "construct_service"
    description = (
        "Construct a service for deployment in Seal system."
        'Input to the tool should be a json with 3 keys: "user_query", "existing_services", and "related_template".'
        'The value of "user_query" should be the description of a deployment task.'
        'On creation, the value of "existing_services" should be all existing services in json format.'
        'On upgrade, the value of "existing_services" should only contain the service about to upgrade.'
        'The value of "related_template" should be related Seal template with version and schema in json format.'
        "The output can be passed to an API controller that can format it into web request and return the response."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise e
        query = data.get("user_query")
        existing_services = data.get("existing_services")
        related_template = data.get("related_template")
        prompt = PromptTemplate(
            template=CONSTRUCT_SERVICE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "context": json.dumps(config.CONFIG.context.__dict__),
                "existing_services": json.dumps(existing_services),
                "related_template": json.dumps(related_template),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(json.dumps(query)).strip()

    async def _arun(self, text: str) -> str:
        raise NotImplementedError()
