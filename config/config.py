from utils import utils
import urllib3

from seal.client import SealClient

from pydantic import BaseModel
from dotenv import load_dotenv

class Context(BaseModel):
    project_id: str = ""
    project_name: str = ""
    environment_id: str = ""
    environment_name: str = ""


class Config(BaseModel):
    openai_api_key: str
    seal_api_key: str
    seal_url: str
    natural_language: str
    show_reasoning: bool
    verbose: bool
    skip_tls_verify: bool
    context: Context


CONFIG: Config


def init():
    load_dotenv()
    openai_api_key =  utils.get_env("OPENAI_API_KEY")
    seal_api_key =  utils.get_env("SEAL_API_KEY")
    seal_url =  utils.get_env("SEAL_URL")
    natural_language = utils.get_env("NATURAL_LANGUAGE","English")
    show_reasoning = utils.get_env_bool("SHOW_REASONING", True)
    verbose = utils.get_env_bool("VERBOSE", False)
    skip_tls_verify = utils.get_env_bool("SKIP_TLS_VERIFY", False)

    if skip_tls_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if not seal_url:
        raise Exception("SEAL_URL is not set")
    if not seal_api_key:
        raise Exception("SEAL_API_KEY is not set")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY is not set")

    global CONFIG
    context = _default_context(seal_url, seal_api_key)
    CONFIG = Config(openai_api_key=openai_api_key, seal_api_key=seal_api_key, seal_url=seal_url,natural_language=natural_language,show_reasoning=show_reasoning,verbose=verbose,skip_tls_verify=skip_tls_verify, context=context)


def set_verbose(verbose: bool):
    global CONFIG
    CONFIG.verbose = verbose


def set_show_reasoning(show_reasoning: bool):
    global CONFIG
    CONFIG.show_reasoning = show_reasoning

def update_context(context: Context):
    global CONFIG
    CONFIG.context = context


def _default_context(seal_url: str, seal_api_key: str) -> Context:
    seal_client = SealClient(
        seal_url,
        seal_api_key,
        verify=False,
    )
    context = Context()
    projects = seal_client.list_projects()
    if len(projects) > 0:
        project = projects[0]
        context = Context(
            project_id=project["id"],
            project_name=project["name"],
        )
    else:
        # no project found
        return context

    environments = seal_client.list_environments(context.project_id)
    if len(environments) > 0:
        environment = environments[0]
        context.environment_id = environment["id"]
        context.environment_name = environment["name"]
    return context
