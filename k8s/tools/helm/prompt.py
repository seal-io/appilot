CONSTRUCT_HELM_OVERRIDED_VALUES = """
You will be provided the default values of a helm chart, and a user query describing a deployment task.

Output overrided values(in yaml) for the helm installation to satisfy the user query.

USER QUERY:
{query}

DEFAULT VALUES:
{default_values}

OVERRIDED VALUES:
"""

CONSTRUCT_HELM_UPGRADE_VALUES = """
You will be provided the default values of a helm chart, previous values of a helm release, and a user query describing an upgrade task.

Output values(in yaml) used for the helm upgrade to satisfy the user query. Keep the previous values in the output as much as possible if they are not changed in the user query.

USER QUERY:
{query}

DEFAULT VALUES:
{default_values}

PREVIOUS VALUES:
{previous_values}

VALUES FOR UPGRADE:
"""
