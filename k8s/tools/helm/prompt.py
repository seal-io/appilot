CONSTRUCT_RESOURCES_TO_CREATE_PROMPT = """
You are a planner that constructs kubernetes resources given a user query describing a deployment task.

You should:
1) evaluate whether kubernetes resources can be constructed according to the user query. If no, say why.
2) if yes, output in the following format:

CONSTRUCTED RESOURCES: 
<KUBERNETES_RESOURCES_IN_YAML>

Strictly follow the above output format, do not add extra explanation or words.
The output will be applied to a kubernetes cluster for creation.

User query: {query}

CONSTRUCTED RESOURCES: 
"""

EXTRACT_KEYWORD_PROMPT = """
You will be provided a user query describing a deployment task. You need to extract the keyword used to seach available helm charts for the deployment.

Example:
User query: deploy a HA mysql.

keyword: 
mysql

---

User query: {query}

keyword:
"""

CONSTRUCT_RESOURCES_TO_UPDATE_PROMPT = """
You are a planner that constructs the expected service object given a user query describing an upgrade task.
For your reference, you will be provided the service about to upgrade and related template version if there's any in the environment. Choose a template and fill in the input variables for the service.

You should:
1) evaluate whether the service object can be constructed according to the user query. If no, say why.
2) if yes, output in the following format:

CONSTRUCTED SERVICE: <SERVICE_OBJECT_IN_ONE_LINE_JSON>

Strictly follow the above output format, do not add extra explanation or words.
Service id is required.
Environment info is required.
Service status is not needed.
The output will be used in the update API call of the service.

Example:

CONSTRUCTED SERVICE: {{"name":"example","template":{{"name":"webservice","version":"0.0.4"}},"environment":{{"id":"1234567"}},"attributes":{{"image":"nginx","ports":[80],"request_cpu":"0.1","request_memory":"128Mi"}}}}

----

Context: {context}
User query: {query}

CURRENT SERVICE:
{current_service}

RELATED TEMPLATE:
{related_template}

"""
