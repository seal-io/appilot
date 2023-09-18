import json
import logging
import os
import re
import subprocess
from langchain import LLMChain, PromptTemplate
from langchain.agents.tools import BaseTool
import requests
import yaml
from config import config
from langchain.schema.language_model import BaseLanguageModel
from k8s.tools.helm.prompt import (
    CONSTRUCT_HELM_OVERRIDED_VALUES,
    CONSTRUCT_HELM_UPGRADE_VALUES,
)
from tools.base.tools import RequireApprovalTool
from kubernetes import config, dynamic, client
from kubernetes.client import api_client

logger = logging.getLogger(__name__)


def remove_empty_lines_and_comments(input_string):
    cleaned_string = re.sub(r"^\s*#.*$", "", input_string, flags=re.MULTILINE)
    cleaned_string = re.sub(r"\n\s*\n", "\n", cleaned_string)
    cleaned_string = cleaned_string.strip()

    return cleaned_string


def get_chart_default_values(chart_url: str):
    """Get default values(in yaml) of a helm chart."""
    helm_show_values_command = f"helm show values {chart_url}"

    try:
        output = subprocess.check_output(
            helm_show_values_command, shell=True, universal_newlines=True
        )

        return remove_empty_lines_and_comments(output)
    except subprocess.CalledProcessError as e:
        return f"Helm show values failed: {e}"
    except Exception as e:
        return f"Error: {e}"


def get_helm_release_values(namespace: str, name: str):
    """Get values of a helm release."""
    helm_get_values_command = f"helm get values {name} -o yaml"

    if namespace:
        helm_get_values_command += f" --namespace {namespace}"

    try:
        output = subprocess.check_output(
            helm_get_values_command, shell=True, universal_newlines=True
        )

        return output
    except subprocess.CalledProcessError as e:
        return f"Helm get values failed: {e}"
    except Exception as e:
        return f"Error: {e}"


def searchChart(keyword: str):
    """Search helm charts in Artifact Hub. Returns a matching chart object."""
    params = {
        "facets": "false",
        "verified_publisher": "true",
        "kind": 0,
        "sort": "relevance",
        # "org": ["bitnami"],
        "ts_query_web": keyword,
    }
    response = requests.get(
        "https://artifacthub.io/api/v1/packages/search", params=params
    )
    if response.status_code >= 400:
        raise Exception("failed to search helm charts: " + response.text)

    data = response.json()
    if len(data.get("packages")) == 0:
        raise Exception("no matching helm chart found")

    chart_name = data.get("packages")[0].get("name")
    repository_name = data.get("packages")[0].get("repository").get("name")
    version = data.get("packages")[0].get("version")

    response = requests.get(
        f"https://artifacthub.io/api/v1/packages/helm/{repository_name}/{chart_name}/{version}",
    )
    chart_raw = response.json()

    chart = {}
    chart["name"] = chart_raw.get("name")
    chart["version"] = chart_raw.get("version")
    chart["description"] = chart_raw.get("description")
    chart["content_url"] = chart_raw.get("content_url")
    return chart


class SearchChartTool(BaseTool):
    """Tool to search helm charts in Artifact Hub. Returns a matching chart object."""

    name = "search_helm_chart"
    description = (
        "Search helm charts in Artifact Hub. "
        'Input should be a json string with two keys, "user_query", "keyword".'
        '"user_query" is the description of the deployment task.'
        '"keyword" is the keyword to search helm charts.'
        "Output a matching chart and overrided values for the helm deployment."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        input = json.loads(text)
        query = input.get("user_query")
        keyword = input.get("keyword")
        chart = searchChart(keyword)

        default_values = get_chart_default_values(chart.get("content_url"))

        prompt = PromptTemplate(
            template=CONSTRUCT_HELM_OVERRIDED_VALUES,
            input_variables=["query"],
            partial_variables={"default_values": default_values},
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        overrided_values = chain.run(query).strip()
        chart["overrided_values"] = yaml.safe_load(overrided_values)
        return json.dumps(chart)


class DeployApplicationTool(RequireApprovalTool):
    """Tool to deploy an application using helm charts."""

    name = "deploy_application"
    description = (
        "Deploy an application using helm charts."
        'Input should be a json string with four keys, "namespace", "name", "chart_url", "values".'
        '"namespace" is the namespace to deploy the application.'
        '"name" is the name of the application, generate a reasonable one if not specified.'
        '"chart_url" is the url to download the helm chart.'
        '"values" is overrided values for the helm installation to satisfy user query.'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        chart_url = input.get("chart_url")
        name = input.get("name")
        namespace = input.get("namespace")
        helm_install_command = f"helm install {name} {chart_url}"

        if namespace != "":
            helm_install_command += f" --namespace {namespace}"

        values = input.get("values")
        if values:
            # add chart_url to values as metadata until https://github.com/helm/helm/issues/4256 is resolved.
            values["metadata_chart_url"] = chart_url

            output_directory = "/tmp/appilot"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            file_path = f"{output_directory}/values.yaml"
            with open(file_path, "w") as file:
                yaml.dump(input.get("values"), file)
            helm_install_command += f" -f {file_path}"

        try:
            output = subprocess.check_output(
                helm_install_command, shell=True, universal_newlines=True
            )

            logger.debug(f"helm install output: {output}")
            return f"application {name} is deployed."
        except subprocess.CalledProcessError as e:
            return f"Helm install failed: {e}"
        except Exception as e:
            return f"Error: {e}"


class GenerateUpgradeApplicationValuesTool(BaseTool):
    """Tool to generate values for upgrading an application."""

    name = "generate_upgrade_application_values"
    description = (
        "Generate values for upgrading an application."
        'Input should be a json string with three keys, "namespace", "name", "user_query".'
        '"namespace" is the namespace of the application.'
        '"name" is the name of the application.'
        '"user_query" is the description of the deployment task.'
        "Output overrided values for the helm upgrade."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        input = json.loads(text)
        namespace = input.get("namespace")
        name = input.get("name")
        query = input.get("user_query")

        helm_values_command = f"helm get values {name}"

        if namespace != "":
            helm_values_command += f" --namespace {namespace}"

        previous_values = get_helm_release_values(namespace, name)

        chart_url = yaml.safe_load(previous_values).get("metadata_chart_url")
        if not chart_url:
            return "Missing chart_url metadata in previous release"

        default_values = get_chart_default_values(chart_url)

        prompt = PromptTemplate(
            template=CONSTRUCT_HELM_UPGRADE_VALUES,
            input_variables=["query"],
            partial_variables={
                "default_values": default_values,
                "previous_values": previous_values,
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        overrided_values_yaml = chain.run(query).strip()

        overrided_values = yaml.safe_load(overrided_values_yaml)
        if "metadata_chart_url" in overrided_values:
            del overrided_values["metadata_chart_url"]

        return json.dumps(overrided_values)


class UpgradeApplicationTool(RequireApprovalTool):
    """Tool to upgrade an application."""

    name = "upgrade_application"
    description = (
        "Upgrade an application."
        'Input should be a json string with three keys, "namespace", "name", "values".'
        '"namespace" is the namespace to deploy the application.'
        '"name" is the name of the application, generate a reasonable one if not specified.'
        '"values" is overrided values for helm upgrade to satisfy user query.'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        namespace = input.get("namespace")
        name = input.get("name")
        values = input.get("values")

        previous_values = get_helm_release_values(namespace, name)

        chart_url = yaml.safe_load(previous_values).get("metadata_chart_url")
        if not chart_url:
            return "Missing chart_url metadata in previous release"

        helm_upgrade_command = f"helm upgrade {name} {chart_url}"

        if namespace != "":
            helm_upgrade_command += f" --namespace {namespace}"

        if values:
            # add chart_url to values as metadata until https://github.com/helm/helm/issues/4256 is resolved.
            values["metadata_chart_url"] = chart_url

            output_directory = "/tmp/appilot"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            file_path = f"{output_directory}/values.yaml"
            with open(file_path, "w") as file:
                yaml.dump(values, file)
            helm_upgrade_command += f" -f {file_path}"

        try:
            output = subprocess.check_output(
                helm_upgrade_command, shell=True, universal_newlines=True
            )

            logger.debug(f"helm upgrade output: {output}")
            return f"application {name} is upgraded."
        except subprocess.CalledProcessError as e:
            return f"Helm upgrade failed: {e}"
        except Exception as e:
            return f"Error: {e}"


def get_pod_ready_status_of_helm_release(name: str, namespace: str) -> str:
    helm_list_command = f"helm get manifest {name}"

    if namespace != "":
        helm_list_command += f" --namespace {namespace}"

    try:
        output = subprocess.check_output(
            helm_list_command, shell=True, universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        return f"Failed to get helm manifest: {e}"
    except Exception as e:
        return f"Error: {e}"

    resource_manifests = yaml.safe_load_all(output)

    dyn_client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )

    replicas = 0
    ready_replicas = 0
    for resource_manifest in resource_manifests:
        if not resource_manifest:
            continue
        resource_kind = resource_manifest.get("kind")
        if resource_kind not in ["Deployment", "StatefulSet", "DaemonSet"]:
            continue

        resoruce_client = dyn_client.resources.get(
            api_version=resource_manifest.get("apiVersion"),
            kind=resource_kind,
        )
        resource = resoruce_client.get(
            name=resource_manifest.get("metadata").get("name"),
            namespace=namespace,
        )

        if resource_kind == "Deployment":
            replicas += resource.get("spec").get("replicas", 0)
            ready_replicas += resource.get("status").get("readyReplicas", 0)
        elif resource_kind == "StatefulSet":
            replicas += resource.get("spec").get("replicas", 0)
            ready_replicas += resource.get("status").get("readyReplicas", 0)
        elif resource_kind == "DaemonSet":
            replicas += resource.get("status").get("desiredNumberScheduled", 0)
            ready_replicas += resource.get("status").get("numberReady", 0)

    return f"{ready_replicas}/{replicas}"


def get_resource_pods(dyn_client, namespace, resource):
    selector = resource.spec.selector.match_labels
    pod_client = dyn_client.resources.get(
        api_version="v1",
        kind="Pod",
    )
    pods = pod_client.get(
        namespace=namespace,
        label_selector=selector,
    )
    return pods.to_dict()


def get_service_endpoints(service):
    service_endpoints = []
    if service.spec.type == "NodePort":
        node_ip = get_node_ip()
        for port in service.spec.ports:
            service_endpoints.append(
                {
                    "name": f"{service.metadata.name}/{port.name}",
                    "endpoint": f"{node_ip}:{port.nodePort}",
                }
            )
    elif service.spec.type == "LoadBalancer":
        for ingress in service.status.load_balancer.ingress:
            if ingress.hostname != "":
                service_endpoints.append(
                    {
                        "name": service.name,
                        "endpoint": ingress.hostname,
                    }
                )
            elif ingress.ip != "":
                service_endpoints.append(
                    {
                        "name": service.name,
                        "endpoint": ingress.ip,
                    }
                )

    return service_endpoints


def get_ingress_endpoints(ingress):
    ingress_endpoints = []
    host = ""
    if ingress.status.load_balancer:
        for ing in ingress.status.load_balancer.ingress:
            if ing.hostname != "":
                host = ing.hostname
            else:
                host = ing.ip

    tlsHosts = []
    if ingress.spec.tls:
        for tls in ingress.spec.tls:
            tlsHosts.extend(tls.hosts)

    if ingress.spec.rules:
        for rule in ingress.spec.rules:
            scheme = "http"
            if rule.host in tlsHosts:
                scheme = "https"
            if rule.host != "":
                host = rule.host
            if host == "":
                continue
            if rule.http:
                for path in rule.http.paths:
                    if path.path != "":
                        ingress_endpoints.append(
                            {
                                "name": f"{ingress.name}/{path.path}",
                                "endpoint": f"{scheme}://{host}{path.path}",
                            }
                        )
                    else:
                        ingress_endpoints.append(
                            {
                                "name": f"{ingress.name}",
                                "endpoint": f"{scheme}://{host}",
                            }
                        )

    return ingress_endpoints


def get_node_ip() -> str:
    config.load_kube_config()
    core_v1 = client.CoreV1Api()
    nodes = core_v1.list_node()
    if nodes.items:
        node = nodes.items[0]
        for address in node.status.addresses:
            if address.type == "ExternalIP":
                return address.address
            elif address.type == "InternalIP":
                ip = address.address
        return ip

    raise Exception("No node found.")


def tidy_up_resource(resource):
    try:
        # make prompt short.
        del resource["metadata"]["managedFields"]
        del resource["metadata"]["resourceVersion"]
        del resource["metadata"]["uid"]
        del resource["metadata"]["generation"]
    except KeyError:
        pass


class ListApplicationsTool(BaseTool):
    """Tool to list applications."""

    name = "list_applications"
    description = (
        "List applications."
        'Input should be a json string with one keys, "namespace".'
        "namespace can be empty if not specified. If namespace is empty, list in current namespace."
        "If namespace is --all, list applications in all namespaces."
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        namespace = input.get("namespace")

        helm_list_command = "helm list --all -o json"

        if namespace == "--all":
            helm_list_command += " --all-namespaces"
        elif namespace != "":
            helm_list_command += f" --namespace {namespace}"

        try:
            output = subprocess.check_output(
                helm_list_command, shell=True, universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            return f"Helm list failed: {e}"
        except Exception as e:
            return f"Error: {e}"

        helm_releases = json.loads(output)
        for helm_release in helm_releases:
            del helm_release["chart"]
            del helm_release["app_version"]
            helm_release["ready"] = get_pod_ready_status_of_helm_release(
                helm_release.get("name"), helm_release.get("namespace")
            )
        return json.dumps(helm_releases)


class GetApplicationResourcesTool(BaseTool):
    """Tool to get application resources."""

    name = "get_application_resources"
    description = (
        "Get application resources. "
        "Helpful to know what resources an application consists of, what status they are in."
        'Input should be a json string with two keys: "name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        name = input.get("name")
        namespace = input.get("namespace")

        helm_manifest_command = f"helm get manifest {name}"

        if namespace != "":
            helm_manifest_command += f" --namespace {namespace}"

        try:
            output = subprocess.check_output(
                helm_manifest_command, shell=True, universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            return f"Helm delete failed: {e}"
        except Exception as e:
            return f"Error: {e}"

        resource_manifests = yaml.safe_load_all(output)

        dyn_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )

        resources = []
        for resource_manifest in resource_manifests:
            resource_kind = resource_manifest.get("kind")
            resoruce_client = dyn_client.resources.get(
                api_version=resource_manifest.get("apiVersion"),
                kind=resource_kind,
            )
            resource = resoruce_client.get(
                name=resource_manifest.get("metadata").get("name"),
                namespace=namespace,
            )
            if resource_kind in ["Deployment", "StatefulSet", "DaemonSet"]:
                pods = get_resource_pods(dyn_client, namespace, resource)
                resources.extend(pods)
            resource = resource.to_dict()
            tidy_up_resource(resource)
            resources.append(resource)

        return json.dumps(resources)


class GetApplicationAccessEndpointsTool(BaseTool):
    """Tool to get application access endpoints."""

    name = "get_application_access_endpoints"
    description = (
        "Get application access endpoints. "
        'Input should be a json string with two keys: "name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        name = input.get("name")
        namespace = input.get("namespace")

        helm_manifest_command = f"helm get manifest {name}"

        if namespace != "":
            helm_manifest_command += f" --namespace {namespace}"

        try:
            output = subprocess.check_output(
                helm_manifest_command, shell=True, universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            return f"Helm delete failed: {e}"
        except Exception as e:
            return f"Error: {e}"

        resource_manifests = yaml.safe_load_all(output)

        dyn_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )

        endpoints = []
        for resource_manifest in resource_manifests:
            resource_kind = resource_manifest.get("kind")
            if resource_kind not in ["Service", "Ingress"]:
                continue

            resoruce_client = dyn_client.resources.get(
                api_version=resource_manifest.get("apiVersion"),
                kind=resource_kind,
            )
            resource = resoruce_client.get(
                name=resource_manifest.get("metadata").get("name"),
                namespace=namespace,
            )

            if resource_kind == "Service":
                endpoints.extend(get_service_endpoints(resource))
            elif resource_kind == "Ingress":
                endpoints.extend(get_ingress_endpoints(resource))

        return json.dumps(endpoints)


class GetApplicationDetailTool(BaseTool):
    """Tool to get application detail."""

    name = "get_application_detail"
    description = (
        "Get application detail. "
        'Input should be a json string with two keys: "name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        name = input.get("name")
        namespace = input.get("namespace")

        helm_status_command = f"helm status {name} --show-resources"

        if namespace != "":
            helm_status_command += f" --namespace {namespace}"

        try:
            output = subprocess.check_output(
                helm_status_command, shell=True, universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            return f"Helm status failed: {e}"
        except Exception as e:
            return f"Error: {e}"

        # Trim NOTES
        index = output.find("NOTES:")

        if index != -1:
            output = output[:index]

        return output


class DeleteApplicationTool(RequireApprovalTool):
    """Tool to delete an application."""

    name = "delete_application"
    description = (
        "Delete an application. "
        'Input should be a json string with two keys: "name" and "namespace".'
    )

    def _run(self, text: str) -> str:
        input = json.loads(text)
        name = input.get("name")
        namespace = input.get("namespace")

        helm_delete_command = f"helm delete {name}"

        if namespace != "":
            helm_delete_command += f" --namespace {namespace}"

        try:
            output = subprocess.check_output(
                helm_delete_command, shell=True, universal_newlines=True
            )

            logger.debug(f"helm delete output: {output}")
            return "Application is deleted."
        except subprocess.CalledProcessError as e:
            return f"Helm delete failed: {e}"
        except Exception as e:
            return f"Error: {e}"
