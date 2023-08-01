import json
from langchain import LLMChain

from langchain.agents.tools import Tool
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from config import config
from seal.client import SealClient
from tools.construct_service.prompt import (
    CONSTRUCT_SERVICE_PROMPT,
)


def _create_construct_service_tool(llm: BaseLanguageModel, client: SealClient) -> Tool:
    services = client.list_services("471708498741178889", "471708821736141321")
    prompt = PromptTemplate(
        template=CONSTRUCT_SERVICE_PROMPT,
        input_variables=["query"],
        partial_variables={
            "services": json.dumps(services),
        },
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    tool = Tool(
        name="construct_service",
        description=(
            "Construct a service for deployment in Seal system."
            'Input to the tool should be a json string with 3 keys: "user_query", "existing_services", and "related_template".'
            'The value of "user_query" should be the description of a deployment task.'
            'The value of "existing_services" should be existing services in json.'
            'The value of "related_template" should be related Seal template with version and schema in json.'
            "The output can be passed to an API controller that can format it into web request and return the response."
        ),
        func=chain.run,
    )
    tool.run
    return tool


class ConstructServiceTool(BaseTool):
    """Construct a service for deployment in Seal system."""

    name = "construct_service"
    description = (
        "Construct a service for deployment in Seal system."
        'Input to the tool should be a json string with 3 keys: "user_query", "existing_services", and "related_template".'
        'The value of "user_query" should be the description of a deployment task.'
        'The value of "existing_services" should be existing services in json format.'
        'The value of "related_template" should be related Seal template with version and schema in json format.'
        "The output can be passed to an API controller that can format it into web request and return the response."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise e
        query = data.get("user_query")
        existing_services = data.get("existing_services")
        related_template = data.get("related_template")
        prompt = PromptTemplate(
            template=CONSTRUCT_SERVICE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "context": json.dumps(config.Config.context.__dict__),
                "existing_services": json.dumps(existing_services),
                "related_template": json.dumps(related_template),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(json.dumps(query)).strip()

    async def _arun(self, text: str) -> str:
        raise NotImplementedError()
