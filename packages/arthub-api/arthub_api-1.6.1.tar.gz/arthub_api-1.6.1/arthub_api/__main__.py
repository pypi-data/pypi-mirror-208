import os
import logging
import logging.handlers
from . import arthub_api_config
from . import cli
from . import utils


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


def init_config():
    setup_logging()
    patch_config()
    load_config()


def main():
    init_config()
    cli.cli()


if __name__ == '__main__':
    main()
