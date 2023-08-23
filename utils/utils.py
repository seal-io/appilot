import os

from i18n import text

from colorama import Fore, Style
from rich.markdown import Markdown
from rich.console import Console

console = Console()


def get_env(key: str, default: str = "") -> str:
    env = os.getenv(key)
    if env is None:
        return default
    return env.strip()


def get_env_bool(key: str, default: bool = False) -> bool:
    env = os.getenv(key)
    if env is None:
        return default
    else:
        return env.lower() in ["1", "true", "yes", "on"]


def print_ai_reasoning(message):
    print(Fore.CYAN + text.get("ai_reasoning") + message + Style.RESET_ALL)


def print_ai_response(message):
    print(text.get("response_prefix"), end="")
    console.print(Markdown(message))
