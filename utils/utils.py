import os


def verbose():
    verbose_env = os.getenv("VERBOSE")
    if verbose_env is not None:
        verbose_value = verbose_env.lower() in ["1", "true", "yes", "on"]
    else:
        verbose_value = False
    return verbose_value
