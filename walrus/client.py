import json
from typing import List
import requests


class WalrusClient:
    """HTTP client for Walrus API."""

    def __init__(self, api_url: str, api_key: str, **kwargs):
        self.api_url = api_url
        self.api_key = api_key
        self.request_args = kwargs

    def headers(self):
        """Get default headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def list_projects(self):
        """List projects."""
        response = requests.get(
            url=self.api_url + "/v1/projects",
            params={"perPage": -1},
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list projects: {response.text}")

        return response.json()["items"]

    def get_project(self, project: str):
        """Get a project by id or name."""
        response = requests.get(
            url=self.api_url + f"/v1/projects/{project}",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get project {project}: {response.text}"
            )

        return response.json()

    def list_environments(self, project_id: str):
        """List environments."""
        params = {
            "perPage": -1,
        }
        response = requests.get(
            url=self.api_url + f"/v1/projects/{project_id}/environments",
            params=params,
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list environments: {response.text}")

        return response.json()["items"]

    def get_environment(self, project_id: str, environment: str):
        """Get an environment by id or name."""
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment}",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get environment {environment}: {response.text}"
            )

        return response.json()

    def delete_environments(self, project_id: str, ids: List[str]):
        """Delete one or multiple environments."""
        items = []
        for id in ids:
            items.append({"id": id})

        body = {"items": items}
        response = requests.delete(
            url=self.api_url + f"/v1/projects/{project_id}/environments",
            headers=self.headers(),
            json=body,
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to delete environment: {response.text}")

        return response.text

    def get_environment_graph(self, project_id: str, environment_id: str):
        """Get environment dependency graph."""
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/graph",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get environment dependency graph: {response.text}"
            )

        return response.text

    def list_services(self, project_id: str, environment_id: str):
        """List services in a project and environment."""
        params = {
            "perPage": -1,
        }

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            params=params,
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list services: {response.text}")

        return response.json()["items"]

    def list_services_in_all_environments(self, project_id: str):
        """List services in all environments of a project."""
        params = {
            "perPage": -1,
        }

        services = []
        envs = self.list_environments(project_id)
        for env in envs:
            response = requests.get(
                url=self.api_url
                + f"/v1/projects/{project_id}/environments/{env['id']}/services",
                params=params,
                headers=self.headers(),
                **self.request_args,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to list services: {response.text}")
            services.extend(response.json()["items"])

        return services

    def get_service_by_name(
        self, project_id: str, environment_id: str, service_name: str
    ):
        """Get a service by name."""

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_name}",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get service: {response.text}")

        return response.text

    def create_service(self, project_id: str, environment_id: str, data):
        """Create a service in a project and environment."""

        response = requests.post(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            headers=self.headers(),
            data=data,
            **self.request_args,
        )
        if response.status_code != 201:
            raise Exception(f"Failed to create service: {response.text}")

        return response.text

    def update_service(self, project_id: str, environment_id: str, data):
        """Update a service in a project and environment."""
        try:
            service = json.loads(data)
        except json.JSONDecodeError as e:
            raise e

        response = requests.put(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service['id']}/upgrade",
            headers=self.headers(),
            data=data,
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to update service: {response.text}")

        return response.text

    def delete_services(
        self, project_id: str, environment_id: str, ids: List[str]
    ):
        """Delete one or multiple services."""
        items = []
        for id in ids:
            items.append({"id": id})

        body = {"items": items}
        response = requests.delete(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services",
            headers=self.headers(),
            json=body,
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to delete service: {response.text}")

        return response.text

    def get_service_access_endpoints(
        self, project_id: str, environment_id: str, service_id: str
    ):
        """Get access endpoints of a service."""
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/access-endpoints",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get service access endpoints: {response.text}"
            )

        return response.text

    def list_service_resources(
        self, project_id: str, environment_id: str, service_id: str
    ):
        """List resources of a service."""
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get service resources: {response.text}"
            )

        return response.json()["items"]

    def get_service_resource_keys(
        self,
        project_id: str,
        environment_id: str,
        service_id: str,
        service_resource_id: str,
    ):
        """Get keys of a service resource."""
        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources/{service_resource_id}/keys",
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get service resource keys: {response.text}"
            )

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

        response = requests.get(
            url=self.api_url
            + f"/v1/projects/{project_id}/environments/{environment_id}/services/{service_id}/resources/{service_resource_id}/log",
            params=params,
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get service resource logs: {response.text}"
            )

        return response.text

    def list_templates(self):
        """List templates."""
        response = requests.get(
            url=self.api_url + "/v1/templates",
            params={"perPage": -1},
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list templates: {response.text}")

        templates = response.json()["items"]
        for template in templates:
            del template["createTime"]
            del template["updateTime"]
            del template["status"]
            del template["source"]
        return json.dumps(templates)

    def get_template_version(self, template: str):
        """Get latest template version given template id or name."""
        response = requests.get(
            url=self.api_url + f"/v1/templates/{template}/versions",
            params={"perPage": -1},
            headers=self.headers(),
            **self.request_args,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to list template versions: {response.text}"
            )

        template_versions = response.json()["items"]
        if len(template_versions) == 0:
            raise Exception("Template version not found")

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
