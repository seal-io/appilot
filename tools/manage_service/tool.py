import asyncio
import json
import threading
import time

from utils import utils
from config import config
from i18n import text
from walrus.client import WalrusClient
from langchain.agents.tools import BaseTool
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from tools.base.tools import RequireApprovalTool
from langchain.callbacks.base import AsyncCallbackHandler
from tools.manage_service.prompt import (
    CONSTRUCT_SERVICE_TO_CREATE_PROMPT,
    CONSTRUCT_SERVICE_TO_UPDATE_PROMPT,
)


class ListServicesTool(BaseTool):
    """Tool to list services."""

    name = "list_services"
    description = "List services in current environment."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            services = self.walrus_client.list_services(
                project_id, environment_id
            )
        except Exception as e:
            return e

        if services is not None and len(services) > 0:
            return json.dumps(services)

        return "No services found."


class WatchServicesTool(BaseTool):
    """Tool to watch services."""

    name = "watch_services"
    description = "Watch service changes in current environment."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id

        try:
            self.walrus_client.watch_services(project_id, environment_id)
        except KeyboardInterrupt:
            # Ctrl+C detected. Stopping the request.
            print("")

        return text.get("watch_service_ending")


class InformServiceReadyTool(BaseTool):
    """Tool to inform user when service becomes ready."""

    name = "inform_service_ready"
    description = "Inform user when a service becomes ready. Input should be name or id of a service."
    walrus_client: WalrusClient

    def watch_service_ready(self, input: str):
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        start_time = time.time()
        timeout = 180
        while True:
            time.sleep(3)
            if time.time() - start_time > timeout:
                break
            service = self.walrus_client.get_service_by_name(
                project_id, environment_id, input
            )
            if service.get("status").get("summaryStatus") == "Ready":
                utils.print_ai_inform(
                    text.get("service_ready_message").format(input)
                )
                break

    def _run(self, input: str) -> str:
        threading.Thread(
            target=self.watch_service_ready, args=(input,)
        ).start()
        return text.get("inform_ready_start")


class ListServicesInAllEnvironmentsTool(BaseTool):
    """Tool to list services in all environments."""

    name = "list_services_in_all_environments"
    description = "List services in all environments of current project."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        try:
            services = self.walrus_client.list_services_in_all_environments(
                project_id
            )
        except Exception as e:
            return e

        if services is not None and len(services) > 0:
            return json.dumps(services)

        return "No services found."


class GetServicesTool(BaseTool):
    """Tool to get a service."""

    name = "get_service"
    description = "Get a service object. Input should be a service name."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            service = self.walrus_client.get_service_by_name(
                project_id, environment_id, query
            )
        except Exception as e:
            return e

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
            service = json.loads(text)
        except Exception as e:
            raise e

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            self.walrus_client.create_service(
                project_id, environment_id, service
            )
        except Exception as e:
            return e

        return "Successfully created."


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
        try:
            self.walrus_client.update_service(project_id, environment_id, text)
        except Exception as e:
            return e

        return "Successfully updated."


class DeleteServicesTool(RequireApprovalTool):
    """Tool to delete one or multiple services."""

    name = "delete_services"
    description = 'Delete one or multiple services. Input should be a list of object, each object contains 2 keys, "name" and "id" of a service.'
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        try:
            services = json.loads(query)
        except Exception as e:
            raise e

        ids = [service["id"] for service in services if "id" in service]
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            self.walrus_client.delete_services(project_id, environment_id, ids)
        except Exception as e:
            return e

        return "Successfully deleted."


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
        environment_id = config.CONFIG.context.environment_id
        try:
            endpoints = self.walrus_client.get_service_access_endpoints(
                project_id, environment_id, text
            )
        except Exception as e:
            return e

        return endpoints


class ListServiceResourcesTool(BaseTool):
    """Tool to get resources of a service."""

    name = "get_service_resources"
    description = (
        "Get resources of a service. "
        "Helpful to know what resources a service consists of, what status they are in. what keys they have."
        "Input should be id of a service. "
        "Output resource objects in json format."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            resources = self.walrus_client.list_service_resources(
                project_id, environment_id, text
            )
        except Exception as e:
            return e

        return resources


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


class GetServiceResourceLogsTool(BaseTool):
    """Tool to get logs of a service resource."""

    name = "get_service_resource_logs_for_diagnose"
    description = (
        "Get logs of a service resource. Use when you need to diagnose service error with logs."
        "Before using this tool, you should get keys of the resource first."
        'Input should be a json with 4 keys: "service_id", "service_resource_id", "key", "line_number".'
        '"key" is identity of a service resource\'s component. You can get available keys by listing service resources. '
        '"line_number" is the number of lines of logs to get. defaults to 100 if user does not specify. '
        "Output is log text."
    )
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        try:
            input = json.loads(query)
        except Exception as e:
            raise e
        service_id = input.get("service_id")
        service_resource_id = input.get("service_resource_id")
        key = input.get("key")
        line_number = input.get("line_number", 100)

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            log = self.walrus_client.get_service_resource_logs(
                project_id,
                environment_id,
                service_id,
                service_resource_id,
                key,
                line_number,
            )
        except Exception as e:
            return e

        prefix = text.get("resource_log_prefix")
        return f"{prefix}\n```{log}```"


class GetServiceResourceLogsReturnDirectTool(BaseTool):
    """Tool to get logs of a service resource."""

    name = "get_service_resource_logs_return_direct"
    description = (
        "Get logs of a service resource. The logs will be shown to users directly. Useful when users want to see logs."
        "Before using this tool, you should get keys of the resource first."
        'Input should be a json with 4 keys: "service_id", "service_resource_id", "key", "line_number".'
        '"key" is identity of a service resource\'s component. You can get available keys by listing service resources. '
        '"line_number" is the number of lines of logs to get. defaults to 100 if user does not specify. '
        "Output is log text."
    )
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        try:
            input = json.loads(query)
        except Exception as e:
            raise e
        service_id = input.get("service_id")
        service_resource_id = input.get("service_resource_id")
        key = input.get("key")
        line_number = input.get("line_number", 100)

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        try:
            log = self.walrus_client.get_service_resource_logs(
                project_id,
                environment_id,
                service_id,
                service_resource_id,
                key,
                line_number,
            )
        except Exception as e:
            return e

        prefix = text.get("resource_log_prefix")
        return f"{prefix}\n```{log}```"


class ConstructServiceToCreateTool(BaseTool):
    """Construct a service for deployment in Walrus system."""

    name = "construct_service_to_create"
    description = (
        "Construct a service for creation in Walrus system."
        'Input to the tool should be a json with 3 keys: "user_query" and "related_template_name".'
        'The value of "user_query" should be the description of a deployment task.'
        'The value of "related_template_name" should be name of a template related to the deployment task.'
        "The output is a service object in json. It will be used in the creation of a service."
    )
    llm: BaseLanguageModel
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except Exception as e:
            raise e

        query = data.get("user_query")
        template_name = data.get("related_template_name")

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        existing_services = self.walrus_client.list_services(
            project_id, environment_id
        )
        related_template = self.walrus_client.get_template_version(
            template_name
        )

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
        'Input to the tool should be a json with 3 keys: "user_query", "service_name" and "related_template_name".'
        'The value of "user_query" should be the description of a deployment task.'
        'The value of "service_name" should be name of the service about to update.'
        'The value of "related_template_name" should be name of a template related to the deployment task.'
        "The output is a service object in json. It will be used in the update of a service."
    )
    llm: BaseLanguageModel
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except Exception as e:
            raise e

        query = data.get("user_query")
        service_name = data.get("service_name")
        template_name = data.get("related_template_name")

        project_id = config.CONFIG.context.project_id
        environment_id = config.CONFIG.context.environment_id
        related_template = self.walrus_client.get_template_version(
            template_name
        )
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
