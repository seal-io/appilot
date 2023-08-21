import json
from typing import List
import requests


class WalrusClient:
    """HTTP client for Walrus API."""

    def __init__(self, api_url: str, api_key: str, **kwargs):
        self.api_url = api_url
        self.api_key = api_key
        self.request_args = kwargs

    def list_projects(self):
        """List projects."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url + "/v1/projects",
            params={"perPage": -1},
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to list projects: {response.text}"

        return response.json()["items"]

    def list_environments(self, project_id: str):
        """List environments."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "perPage": -1,
        }
        response = requests.get(
            url=self.api_url + f"/v1/projects/{project_id}/environments",
            params=params,
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to list environments: {response.text}"

        return response.json()["items"]

    def delete_environments(self, project_id: str, ids: List[str]):
        """Delete one or multiple environments."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        items = []
        for id in ids:
            items.append({"id": id})
        # try:
        #     id_list = json.loads(ids)
        # except json.JSONDecodeError as e:
        #     return f"Failed to decode ids: {e}"

        body = {"items": items}
        response = requests.delete(
            url=self.api_url + f"/v1/projects/{project_id}/environments",
            headers=headers,
            json=body,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to delete environment: {response.text}"

        return response.text

    def get_environment_graph(self, project_id: str, environment_id: str):
        """Get environment dependency graph."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/graph",
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return (
                f"Failed to get environment dependency graph: {response.text}"
            )

        return response.text

    def list_services(self, project_id: str, environment_id: str):
        """List services in a project and environment."""
        params = {
            "perPage": -1,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            params=params,
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to list services: {response.text}"

        return response.json()["items"]

    def get_service_by_name(
        self, project_id: str, environment_id: str, service_name: str
    ):
        """Get a service by name."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_name}",
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to get service: {response.text}"

        return response.text

    def create_service(self, project_id: str, environment_id: str, data):
        """Create a service in a project and environment."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.post(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            headers=headers,
            data=data,
            **self.request_args,
        )
        if response.status_code != 201:
            return f"Failed to create service: {response.text}"

        return response.text

    def update_service(self, project_id: str, environment_id: str, data):
        """Update a service in a project and environment."""
        try:
            service = json.loads(data)
        except json.JSONDecodeError as e:
            raise e

        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.put(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service['id']}/upgrade",
            headers=headers,
            data=data,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to update service: {response.text}"

        return response.text

    def delete_services(
        self, project_id: str, environment_id: str, ids: List[str]
    ):
        """Delete one or multiple services."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        items = []
        for id in ids:
            items.append({"id": id})

        body = {"items": items}
        response = requests.delete(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            headers=headers,
            json=body,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to delete service: {response.text}"

        return response.text

    def get_service_access_endpoints(
        self, project_id: str, environment_id: str, service_id: str
    ):
        """Get access endpoints of a service."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/access-endpoints",
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to get service access endpoints: {response.text}"

        return response.text

    def list_service_resources(
        self, project_id: str, environment_id: str, service_id: str
    ):
        """List resources of a service."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources",
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to get service resources: {response.text}"

        return response.json()["items"]

    def get_service_resource_keys(
        self,
        project_id: str,
        environment_id: str,
        service_id: str,
        service_resource_id: str,
    ):
        """Get keys of a service resource."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources/{service_resource_id}/keys",
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to get service resource keys: {response.text}"

        return response.text

    def get_service_resource_logs(
        self,
        project_id: str,
        environment_id: str,
        service_id: str,
        service_resource_id: str,
        key: str,
    ):
        """Get logs of a service resource."""
        params = {
            "key": key,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources/{service_resource_id}/log",
            params=params,
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to get service resource logs: {response.text}"

        return response.text

    def list_templates(self):
        """List templates."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url + "/v1/templates",
            params={"perPage": -1},
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to list templates: {response.text}"

        templates = response.json()["items"]
        for template in templates:
            del template["createTime"]
            del template["updateTime"]
            del template["status"]
            del template["source"]
        return json.dumps(templates)

    def get_template_version(self, id: str):
        """Get latest template version given template id."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            url=self.api_url + f"/v1/templates/{id}/versions",
            params={"templateID": id, "perPage": -1},
            headers=headers,
            **self.request_args,
        )
        if response.status_code != 200:
            return f"Failed to list template versions: {response.text}"

        template_versions = response.json()["items"]
        if len(template_versions) == 0:
            raise Exception(f"Failed to get template version: {response.text}")

        keys_to_remove = [
            "readme",
            "outputs",
            "requiredProviders",
            "createTime",
            "updateTime",
            "id",
            "source",
        ]

        template_version = response.json()["items"][0]
        # remove keys that are not needed to make prompt neat

        for key in keys_to_remove:
            if key in template_version:
                del template_version[key]
            if key in template_version["schema"]:
                del template_version["schema"][key]

        return json.dumps(template_version)
