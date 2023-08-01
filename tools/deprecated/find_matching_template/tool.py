import json
from typing import Optional
from langchain import LLMChain

from langchain.agents.tools import Tool
from langchain.agents.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from tools.find_matching_template.prompt import FIND_TEMPLATE_PROMPT
from seal.client import SealClient


class MatchTemplateTool(BaseTool):
    """Find matching template useful for a deployment task.
    Input should be a deployment task.
    Output matching template id.
    """

    name = "find_matching_template"
    description = (
        "Find a matching template for a deploy/upgrade task."
        "Input should be a deploy/upgrade task."
        "Output matching template id, or None when no matching template found."
    )
    seal_client: SealClient
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        templates = self.seal_client.list_templates()
        prompt = PromptTemplate(
            template=FIND_TEMPLATE_PROMPT,
            input_variables=["query"],
            partial_variables={
                "templates": json.dumps(templates),
            },
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
