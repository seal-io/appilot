from langchain.callbacks import HumanApprovalCallbackHandler
from pydantic import Field


class ApprovalCallbackHandler(HumanApprovalCallbackHandler):
    """Callback for manually approval."""

    tool_name: str = Field(..., description="Name of the tool.")

    def __init__(self, tool_name: str):
        self.tool_name = tool_name  # Field(tool_name)
        super().__init__(approve=self._approve)

    pass

    def _approve(self, _input: str) -> bool:
        msg = (
            "Input: \n"
            f"{_input}"
            "\n"
            f"Action: {self.tool_name}"
            "\n"
            "Do you approve the above action? "
            "Anything except 'Y'/'Yes' (case-insensitive) will be treated as a no."
            "\n"
        )
        resp = input(msg)
        return resp.lower() in ("yes", "y")
