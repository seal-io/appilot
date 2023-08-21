import json
from langchain import LLMChain

from langchain.agents.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from tools.manage_template.prompt import FIND_TEMPLATE_PROMPT
from walrus.client import WalrusClient


class MatchTemplateTool(BaseTool):
    """Find matching template useful for a deployment task.
    Input should be a deployment task.
    Output matching template id.
    """

    name = "find_matching_template"
    description = (
        "Find a matching template for a deploy/upgrade task."
        "Input should be description of the task. For upgrade task, include previous template info."
        "Output matching template id, or None when no matching template found."
    )
    walrus_client: WalrusClient
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        templates = self.walrus_client.list_templates()
        prompt = PromptTemplate(
            template=FIND_TEMPLATE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "templates": json.dumps(templates),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(query)


class GetTemplateSchemaTool(BaseTool):
    """Tool to get template version and schema given template id."""

    name = "get_template_schema"
    description = (
        "Get template version and schema given template id."
        "Input should be a template id."
        "Output template schema."
    )
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        return self.walrus_client.get_template_version(query)
