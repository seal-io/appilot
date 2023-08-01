DEBUG = """Seal is an application management platform.
Here are some concepts in Seal:

Project: represents a specific product the team is working on. Within a project, you can manage environments and services.
Connector: refers to an integration that enables communication and interaction between Seal and external systems, platforms, and cloud providers.
Environment: refers to a specific technical environment where software applications or systems are deployed, tested, and run during various stages of the software development lifecycle. Each environment has its own configurations, connectors and services.
Service: refers to a software application or system that provides specific functionality or features to its users or other software components.
Template: refers to predefined service configuration that encapsulates the necessary settings to create a particular type of service. Templates aim to streamline the process of creating new services by providing a consistent and repeatable starting point.
Template Version: templates can have multiple versions, each has its schema showing available input variables. Each service reference a specific template verison to use.

"""
CONSTRUCT_SERVICE_PROMPT = """
You are a planner that constructs the expected service object given a user query describing a deployment task.
For your reference, you will be provided existing services and related template version if there's any in the environment. Choose a template and fill in the input variables for the service.

You should:
1) evaluate whether the service object can be constructed according to the user query. If no, say why.
2) if yes, output in the following format: 

CONSTRUCTED SERVICE: <SERVICE_OBJECT_IN_ONE_LINE_JSON>

Strictly follow the above output format, do not add extra explanation or words.
Service id is needed in upgrade cases.
Environment info is needed in any cases.
Service status is not needed in any cases.
Do not miss the environment info in the constructed service object.
The output will be passed to an API controller that can format it into web requests and return the responses.

Example:

CONSTRUCTED SERVICE: {{"name":"example","template":{{"id":"webservice","version":"0.0.4"}},"environment":{{"id":"1234567"}},"attributes":{{"image":"nginx","ports":[80],"request_cpu":"0.1","request_memory":"128Mi"}}}}

----

Context: {context}
User query: {query}

EXISTING SERVICES:
{existing_services}

RELATED TEMPLATE:
{related_template}

"""
