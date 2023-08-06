import os
import logging
import logging.handlers

import environ

from . import arthub_api_config
from . import cli
from . import utils


@environ.config(prefix="AH_BLADE")
class DefaultEnvConfig(object):
    """This creates a env config loads from AH_XXXXX and AH_BLADE_XXXX."""
    api_config_name = environ.var(os.getenv("AH_API_CONFIG_NAME"), help="Api config name. one of ['oa', 'qq']")
    public_token = environ.var("",  help="Value for blade public token auth method.")
    account_email = environ.var(os.getenv("AH_ACCOUNT_NAME"),  help="User name for login auth method.")
    password = environ.var(os.getenv("AH_PASSWORD"),  help="User password for login auth method.")


def load_config(file_path=None):
    UserError = type("UserError", (Exception,), {})

    file_path = file_path or os.getenv("ARTHUB_API_CONFIG",
                                       os.path.expanduser("~/Documents/ArtHub/arthub_api_config.py"))
    if not os.path.isfile(file_path):
        return

    mod = {
        "__file__": file_path,
    }

    try:
        with open(file_path) as file_obj:
            exec(compile(file_obj.read(), file_obj.name, "exec"), mod)
    except IOError:
        raise

    except Exception:
        raise UserError("Better double-check your user config.")

    for key in dir(arthub_api_config):
        if key.startswith("__"):
            continue

        try:
            value = mod[key]
        except KeyError:
            continue
        setattr(arthub_api_config, key, value)

    return file_path


def patch_config():
    for member in dir(arthub_api_config):
        if member.startswith("__"):
            continue

        setattr(arthub_api_config, "_%s" % member,
                getattr(arthub_api_config, member))


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # to file
    log_dir = os.path.expanduser("~/Documents/ArtHub/sdk_log")
    if utils.mkdir(log_dir):
        f_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_dir, "arthub_api.log"),
                                                              when='midnight', interval=1,
                                                              backupCount=7)
        f_handler.setLevel(logging.INFO)
        f_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
        logger.addHandler(f_handler)

    # to stdout
    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.DEBUG)
    s_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(s_handler)


def apply_environ_to_config():
    """This loads config from env and set into arthub_api_config."""
    ENV_CONFIG = environ.to_config(DefaultEnvConfig)
    if ENV_CONFIG.api_config_name:
        arthub_api_config.api_config_name = ENV_CONFIG.api_config_name
    if ENV_CONFIG.public_token:
        arthub_api_config.blade_public_token = ENV_CONFIG.public_token
    if ENV_CONFIG.account_email:
        arthub_api_config.account_email = ENV_CONFIG.account_email
    if ENV_CONFIG.password:
        arthub_api_config.password = ENV_CONFIG.password


def init_config():
    setup_logging()
    patch_config()
    load_config()
    apply_environ_to_config()


def main():
    init_config()
    cli.cli()


if __name__ == '__main__':
    main()
