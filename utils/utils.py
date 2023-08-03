import os

from i18n import text

from colorama import Fore, Style

def verbose():
    verbose_env = os.getenv("VERBOSE")
    if verbose_env is not None:
        verbose_value = verbose_env.lower() in ["1", "true", "yes", "on"]
    else:
        verbose_value = False
    return verbose_value

def show_reasoning():
    r_env = os.getenv("SHOW_REASONING")
    if r_env is not None:
        r_value = r_env.lower() in ["1", "true", "yes", "on"]
    else:
        r_value = False
    return r_value

def print_ai_reasoning(message):
    print(Fore.CYAN + text.get("ai_reasoning") + message + Style.RESET_ALL)

def print_ai_response(message):
    print(Fore.WHITE + text.get("response_prefix") + message + Style.RESET_ALL)