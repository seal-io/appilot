from langchain.agents.tools import BaseTool
import webbrowser


class BrowseURLTool(BaseTool):
    """Tool to access a URL in browser."""

    name = "open_url_in_browser"
    description = "Open a URL in browser. Input is a URL."

    def _run(self, url: str) -> str:
        webbrowser.open(url)
        return "The URL is opened in browser."
