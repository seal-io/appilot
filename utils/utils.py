import os
import sys

from i18n import text

from colorama import Fore, Style
from rich.markdown import Markdown
from rich.console import Console
from datetime import datetime
from dateutil import parser
from datetime import timezone

console = Console()

inform_sent = False


def get_env(key: str, default: str = "") -> str:
    env = os.getenv(key)
    if env is None:
        return default
    return env.strip()


def get_env_list(key: str, default: [] = []) -> list[str]:
    env = os.getenv(key)
    if env is None:
        return default
    return [item.strip() for item in env.split(",")]


def get_env_bool(key: str, default: bool = False) -> bool:
    env = os.getenv(key)
    if env is None:
        return default
    else:
        return env.lower() in ["1", "true", "yes", "on"]


def print_ai_reasoning(message):
    print(Fore.CYAN + text.get("ai_reasoning") + message + Style.RESET_ALL)


def print_ai_inform(message):
    global inform_sent
    inform_sent = True
    # move cursor to the end of previous line
    sys.stdout.write("\033[F\033[1000C")
    print(
        Fore.LIGHTYELLOW_EX
        + "\n"
        + text.get("inform_prefix")
        + message
        + Style.RESET_ALL
    )


def is_inform_sent():
    global inform_sent
    if inform_sent:
        inform_sent = False
        return True


def print_ai_response(message):
    print(text.get("response_prefix"), end="")
    console.print(Markdown(message))


def print_rejected_message():
    print(text.get("response_prefix"), end="")
    print(text.get("rejected_message"))


def format_relative_time(iso_time):
    parsed_time = parser.isoparse(iso_time)
    current_time = datetime.now(timezone.utc)
    time_difference = current_time - parsed_time

    days = time_difference.days
    hours = int(time_difference.total_seconds() // 3600)
    minutes = int((time_difference.total_seconds() % 3600) // 60)

    if days > 0:
        return f"{days} Days ago"
    elif hours > 0:
        return f"{hours} Hours ago"
    elif minutes > 0:
        return f"{minutes} Minutes ago"
    else:
        return "Just now"
