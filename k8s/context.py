from typing import Any
from kubernetes import client


API_RESOURCES: list[dict[Any | str, Any]]


class GroupVersionKind:
    """GroupVersionKind."""

    def __init__(self, groupVersion: str, kind: str):
        self.groupVersion = groupVersion
        self.kind = kind


def init_api_resources_cache():
    """Get available api resources. Similar to kubectl api-resources."""

    api_client = client.ApiClient()
    api_resource_list = api_client.call_api(
        "/api/v1",
        "GET",
        response_type="object",
        _return_http_data_only=True,
    )
    api_resources = [
        {**resource, "groupVersion": "v1"}
        for resource in api_resource_list["resources"]
        if "storageVersionHash" in resource
    ]

    api_group_list = api_client.call_api(
        "/apis",
        "GET",
        response_type="object",
        _return_http_data_only=True,
    )

    for api_group in api_group_list["groups"]:
        api_resource_list = api_client.call_api(
            "/apis/" + api_group["preferredVersion"]["groupVersion"],
            "GET",
            response_type="object",
            _return_http_data_only=True,
        )
        api_resources.extend(
            [
                {
                    **resource,
                    "groupVersion": api_group["preferredVersion"][
                        "groupVersion"
                    ],
                }
                for resource in api_resource_list["resources"]
                if "storageVersionHash" in resource and resource["namespaced"]
            ]
        )
    global API_RESOURCES
    API_RESOURCES = api_resources


def get_api_resources():
    return API_RESOURCES


def search_api_resource(resource_kind: str) -> GroupVersionKind:
    api_resources = get_api_resources()
    matching_resources = [
        api_resource
        for api_resource in api_resources
        if str(api_resource["name"]).lower() == resource_kind
        or str(api_resource["singularName"]).lower() == resource_kind
        or str(api_resource["kind"]).lower() == resource_kind
        or (
            "shortNames" in api_resource
            and resource_kind in api_resource["shortNames"]
        )
    ]

    if matching_resources:
        return GroupVersionKind(
            matching_resources[0]["groupVersion"],
            matching_resources[0]["kind"],
        )

    raise Exception(f"Resource {resource_kind} not found.")
