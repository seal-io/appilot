import json
from typing import Any, Dict, Optional, List
from uuid import UUID
import click
import yaml

from i18n import text
from utils import utils
from config import config

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult
from langchain.schema.output import LLMResult
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter


class HumanRejectedException(Exception):
    """Exception to raise when a person manually review and rejects a value."""


def remove_triple_backticks(text):
    if text.startswith("```") and text.endswith("```"):
        lines = text.split("\n")

        if len(lines) <= 1:
            return ""

        lines = lines[1:-1]

        result_text = "\n".join(lines)

        return result_text

    return text


class ApprovalCallbackHandler(BaseCallbackHandler):
    """Callback for manual approval."""

    raise_error: bool = True

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if not self._approve(input_str, serialized):
            raise HumanRejectedException(
                f"Inputs {input_str} to tool {serialized} were rejected."
            )

    def _approve(self, _input: str, serialized: Dict[str, Any]) -> bool:
        message = text.get("ask_approval")
        _input = remove_triple_backticks(_input.strip())

        is_json = False
        try:
            json_input = json.loads(_input)
        except Exception as e:
            # If the input is not a valid JSON, just pass
            pass
        else:
            # Serialize the JSON input with colors
            is_json = True
            json_string = json.dumps(json_input, indent=4)
            _input = highlight(json_string, JsonLexer(), TerminalFormatter())

        if not is_json:
            # Now try YAML
            try:
                yaml.safe_load_all(_input)
            except Exception as e:
                # If the input is not a valid YAML, just pass
                pass
            else:
                # Serialize the YAML input with colors
                _input = highlight(_input, YamlLexer(), TerminalFormatter())

        return click.confirm(
            message.format(input=_input, tool_name=serialized["name"]),
            default=False,
            prompt_suffix="",
        )


class PrintReasoningCallbackHandler(BaseCallbackHandler):
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        if not config.APPILOT_CONFIG.show_reasoning:
            return

        generation_text = response.generations[0][0].text
        lines = generation_text.splitlines()
        reason_prompt_prefix = "Reason:"
        for line in reversed(lines):
            if line.startswith(reason_prompt_prefix):
                reason_text = line.lstrip("Reason:").strip()
                utils.print_ai_reasoning(reason_text)
                break
        """Print AI reasoning."""
