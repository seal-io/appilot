import logging

import urllib3
from utils import utils

from pydantic import BaseModel
from dotenv import load_dotenv


class Config(BaseModel):
    openai_api_key: str
    openai_api_base: str
    natural_language: str
    toolkits: list[str]
    show_reasoning: bool
    verbose: bool


APPILOT_CONFIG: Config


def init():
    load_dotenv()
    openai_api_base = utils.get_env("OPENAI_API_BASE")
    openai_api_key = utils.get_env("OPENAI_API_KEY")
    natural_language = utils.get_env("NATURAL_LANGUAGE", "English")
    toolkits = utils.get_env_list("TOOLKITS")
    show_reasoning = utils.get_env_bool("SHOW_REASONING", True)
    verbose = utils.get_env_bool("VERBOSE", False)

    if not openai_api_key:
        raise Exception("OPENAI_API_KEY is not set")

    if not verbose:
        logging.basicConfig(level=logging.CRITICAL)
        # Disable child loggers of urllib3, e.g. urllib3.connectionpool
        logging.getLogger(urllib3.__package__).propagate = False

    global APPILOT_CONFIG
    APPILOT_CONFIG = Config(
        openai_api_base=openai_api_base,
        openai_api_key=openai_api_key,
        natural_language=natural_language,
        toolkits=toolkits,
        show_reasoning=show_reasoning,
        verbose=verbose,
    )


def set_verbose(verbose: bool):
    global APPILOT_CONFIG
    APPILOT_CONFIG.verbose = verbose


def set_show_reasoning(show_reasoning: bool):
    global APPILOT_CONFIG
    APPILOT_CONFIG.show_reasoning = show_reasoning
