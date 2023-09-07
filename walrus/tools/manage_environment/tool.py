import json
import os
from langchain.agents.tools import BaseTool
from i18n import text
from tools.base.tools import RequireApprovalTool
import pydot
from PIL import Image

from walrus.client import WalrusClient
from walrus import context as walrus_context


class ListEnvironmentsTool(BaseTool):
    """Tool to list environments."""

    name = "list_environments"
    description = (
        "List environments of a project."
        "Input should be a project id or an empty string indicating current project in the context."
    )
    walrus_client: WalrusClient

    def _run(self, project_id: str) -> str:
        if project_id == "":
            project_id = walrus_context.GLOBAL_CONTEXT.project_id
        try:
            environments = self.walrus_client.list_environments(project_id)
        except Exception as e:
            return e
        if environments is not None and len(environments) > 0:
            return json.dumps(environments)
        return "No environments found."


class DeleteEnvironmentsTool(RequireApprovalTool):
    """Tool to delete environments."""

    name = "delete_environments"
    description = 'Delete one or multiple environments. Input should be a list of object, each object contains 2 keys, "name" and "id" of an environment.'
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            environments = json.loads(text)
        except Exception as e:
            raise e

        ids = [env["id"] for env in environments if "id" in env]
        project_id = walrus_context.GLOBAL_CONTEXT.project_id
        try:
            self.walrus_client.delete_environments(project_id, ids)
        except Exception as e:
            return e

        return "Deletion started."


class GetEnvironmentDependencyGraphTool(BaseTool):
    """Tool to get environment dependency graph."""

    name = "get_environment_dependency_graph"
    description = "Get dependency graph of an environment. Input should be name or id of an environment."
    walrus_client: WalrusClient

    def show_graph(self, graph_data: dict):
        node_shape_map = {
            "Service": "box",
            "ServiceResourceGroup": "ellipse",
            "ServiceResource": "ellipse",
        }
        edge_style_map = {
            "Composition": "composition",
            "Realization": "dotted",
            "Dependency": "dashed",
        }

        node_height = 1
        graph = pydot.Dot(graph_type="digraph")
        node_ids = []
        for vertex in graph_data["vertices"]:
            label_suffix = ""
            if vertex["kind"] == "Service":
                label_suffix = "<br/>service"
            else:
                label_suffix = f"<br/>{vertex['extensions']['type']}"

            graph.add_node(
                pydot.Node(
                    name=vertex["id"],
                    label=f"<{vertex['name']}{label_suffix}>",
                    shape=node_shape_map[vertex["kind"]],
                    height=node_height,
                )
            )
            node_ids.append(vertex["id"])

        edge_ids = []
        for edge in graph_data["edges"]:
            # FIXME: This is a hack to avoid edges that are not in the graph. resolve in API.
            if (
                edge.get("start").get("id") not in node_ids
                or edge.get("end").get("id") not in node_ids
            ):
                continue
            # FIXME: This is a hack to avoid duplicate edges. resolve in API.
            edge_id = edge.get("start").get("id") + edge.get("end").get("id")
            if edge_id in edge_ids:
                continue

            graph.add_edge(
                pydot.Edge(
                    edge.get("start").get("id"),
                    edge.get("end").get("id"),
                    style=edge_style_map[edge.get("type")],
                )
            )
            edge_ids.append(edge_id)

        output_directory = "/tmp/appilot"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        image_path = os.path.join(output_directory, "dependency_graph.png")
        graph.write_png(image_path)
        image = Image.open(image_path)
        image.show()

    def _run(self, environment: str) -> str:
        project_id = walrus_context.GLOBAL_CONTEXT.project_id
        if environment is None or environment == "":
            environment = walrus_context.GLOBAL_CONTEXT.environment_id

        graph_data = self.walrus_client.get_environment_graph(
            project_id, environment
        )
        self.show_graph(graph_data)

        return text.get("show_graph_message")


class CloneEnvironmentTool(RequireApprovalTool):
    """Tool to clone an environment."""

    name = "clone_environment"
    description = (
        "Clone an environment to a new one. "
        'Input should be a json string with two keys: "original_environment_name" and "target_environment_name".'
    )

    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except Exception as e:
            return e

        project_id = walrus_context.GLOBAL_CONTEXT.project_id
        original_environment_name = data.get("original_environment_name")
        target_environment_name = data.get("target_environment_name")

        try:
            environment = self.walrus_client.get_environment(
                project_id, original_environment_name
            )
            services = self.walrus_client.list_services(
                project_id, original_environment_name
            )
            environment["name"] = target_environment_name
            environment["services"] = services

            self.walrus_client.create_environment(project_id, environment)
        except Exception as e:
            return e

        return "Successfully cloned."
