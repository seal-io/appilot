import json
import subprocess
import click
from langchain import LLMChain, PromptTemplate
from langchain.agents.tools import BaseTool
import yaml
from config import config
from langchain.schema.language_model import BaseLanguageModel
from k8s.tools.manage_resource.prompt import (
    CONSTRUCT_RESOURCES_TO_CREATE_PROMPT,
)
from tools.base.tools import RequireApprovalTool
from kubernetes import config, dynamic, client
from kubernetes.client import api_client
from k8s import context
from utils import utils
from i18n import text


class ListResourcesTool(BaseTool):
    """Tool to list resources."""

    name = "list_kubernetes_resources"
    description = (
        "List kubernetes resources."
        'Input should be a json string with two keys: "resource_kind" and "namespace".'
        '"namespace" is optional, set it to empty string if user does not specify.'
        "If namespace is --all, lists in all namespaces."
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)

        resource_kind = str(input.get("resource_kind")).lower()
        namespace = str(input.get("namespace")).lower()

        # Use kubectl directly. Raw API output can easily exceed the LLM rate limit.
        kubectl_get_command = f"kubectl get {resource_kind}"

        if namespace == "--all":
            kubectl_get_command += " --all-namespaces"
        elif namespace:
            kubectl_get_command += f" -n {namespace}"

        try:
            output = subprocess.check_output(
                kubectl_get_command, shell=True, universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            return f"kubectl get failed: {e}"
        except Exception as e:
            return f"Error: {e}"

        # Print raw output without markdown rendering
        return f"{utils.raw_format_prefix}\n{output}"


class DeleteResourceTool(RequireApprovalTool):
    """Tool to delete a kubernetes resource."""

    name = "delete_a_kubernetes_resource"
    description = (
        "Delete a kubernetes resource. "
        'Input should be a json string with three keys: "resource_kind", "resource_name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)

        dyn_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )
        resource_kind = input.get("resource_kind")
        resource_name = input.get("resource_name")
        namespace = input.get("namespace", "default")
        gvk = context.search_api_resource(resource_kind)
        resources = dyn_client.resources.get(
            api_version=gvk.groupVersion,
            kind=gvk.kind,
        )

        try:
            resources.delete(name=resource_name, namespace=namespace)
        except Exception as e:
            return f"Error deleting resource: {e}"

        return "Resource is being deleted."


class GetResourceDetailTool(BaseTool):
    """Tool to get detail of a kubernetes resource."""

    name = "get_kubernetes_resource_detail"
    description = (
        "Get detail of a kubernetes resource. "
        'Input should be a json string with three keys: "resource_kind", "resource_name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)

        dyn_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )
        resource_kind = input.get("resource_kind")
        resource_name = input.get("resource_name")
        namespace = input.get("namespace", "default")
        gvk = context.search_api_resource(resource_kind)
        resources = dyn_client.resources.get(
            api_version=gvk.groupVersion,
            kind=gvk.kind,
        )

        try:
            resource = resources.get(name=resource_name, namespace=namespace)
            # make prompt short.
            del resource["metadata"]["managedFields"]
            del resource["metadata"]["resourceVersion"]
            del resource["metadata"]["uid"]
            del resource["metadata"]["generation"]
        except KeyError:
            pass
        except Exception as e:
            return f"Error getting resource detail: {e}"

        return json.dumps(resource.to_dict())


class GetPodLogsTool(BaseTool):
    """Tool to get logs of a pod."""

    name = "get_kubernetes_pod_logs"
    description = (
        "Get logs of a pod. "
        'Input should be a json string with four keys: "name", "namespace", "container_name" and "line_number".'
        '"container_name" is optional. Set it to the name of the container to get logs from.'
        '"line_number" is int defaulting to 50. Set it to the number of lines of logs to return.'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)

        name = input.get("name")
        namespace = input.get("namespace")
        container_name = input.get("container_name", "")
        line_number = input.get("line_number", 50)

        if namespace == "":
            namespace = "default"

        v1 = client.CoreV1Api()

        pod_log = v1.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            container=container_name,
            tail_lines=line_number,
        )

        return f"```\n{pod_log}\n```"


class WatchResourcesTool(BaseTool):
    """Tool to watch resources."""

    name = "watch_resources"
    description = (
        "Watch resources changes in a namespace."
        'Input should be a json string with two keys: "resource_kind" and "namespace".'
    )

    def _run(self, query: str) -> str:
        input = json.loads(query)
        resource_kind = str(input.get("resource_kind")).lower()
        namespace = str(input.get("namespace")).lower()

        if namespace == "":
            namespace = "default"

        kubectl_watch_command = (
            f"kubectl get {resource_kind} -w -n {namespace}"
        )

        try:
            click.echo(text.get("watch_service_note"))
            process = subprocess.Popen(
                kubectl_watch_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            for line in process.stdout:
                print(line, end="")

            process.wait()

        except KeyboardInterrupt:
            # Ctrl+C detected. Stopping the request.
            print("Terminated by user")

        return text.get("watch_service_ending")


class ConstructResourceTool(BaseTool):
    """Tool to construct resources."""

    name = "construct_kubernetes_resources"
    description = (
        "Construct Kubernetes resources. "
        'Input to the tool should be a json with one keys: "user_query".'
        'The value of "user_query" should be the description of a deployment task.'
        "The output is kubernetes resources in yaml format."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        input = json.loads(text)
        query = input.get("user_query")
        prompt = PromptTemplate(
            template=CONSTRUCT_RESOURCES_TO_CREATE_PROMPT,
            input_variables=["query"],
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(json.dumps(query)).strip()


class ApplyResourcesTool(RequireApprovalTool):
    """Tool to apply kubernetes resources."""

    name = "apply_kubernetes_resources"
    description = (
        "Apply kubernetes resources. "
        "Input should be kubernetes resources in yaml format."
        "The provided yaml should is fully functional. Do not provide empty input. "
        "It will be applied to a kubernetes cluster."
    )

    def _run(self, text: str) -> str:
        lines = text.splitlines()
        # remove triple backticks of the yaml text
        filtered_lines = [line for line in lines if not line.startswith("```")]
        filtered_text = "\n".join(filtered_lines)
        try:
            yaml_documents = yaml.safe_load_all(filtered_text)
            apply_or_update_yaml(yaml_documents)
        except Exception as e:
            return f"Error applying/updating YAML manifest: {str(e)}"

        resources = []
        for yaml_manifest in yaml_documents:
            resources.append(
                {
                    "kind": yaml_manifest["kind"],
                    "name": yaml_manifest["metadata"]["name"],
                }
            )

        return f"Applied the following resources: {resources}"


def apply_or_update_yaml(yaml_documents):
    for yaml_manifest in yaml_documents:
        api_version = yaml_manifest["apiVersion"]
        kind = yaml_manifest["kind"]

        config.load_kube_config()
        dynamic_client = dynamic.DynamicClient(client.api_client.ApiClient())
        resource = dynamic_client.resources.get(
            api_version=api_version, kind=kind
        )

        namespace = yaml_manifest.get("metadata", {}).get(
            "namespace", "default"
        )
        name = yaml_manifest.get("metadata", {}).get("name", "")

        resource_exists = False
        try:
            resource.get(namespace=namespace, name=name)
            resource_exists = True
        except Exception as e:
            pass

        # update if exists, else create.
        try:
            if resource_exists:
                resource.patch(
                    namespace=namespace,
                    name=name,
                    body=yaml_manifest,
                )
            else:
                resource.create(namespace=namespace, body=yaml_manifest)
        except Exception as e:
            print(f"Error applying/updating YAML manifest: {str(e)}")
