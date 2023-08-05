import logging
import os

from python_sdk import utils

ENABLE_ON_ACCESS_CONFIG_RELOADING: utils.BoolFlag = utils.BoolFlag(False)


def enable_on_access_config_reloading() -> None:
    ENABLE_ON_ACCESS_CONFIG_RELOADING.set()
    logging.warning(
        "On access config reloading has been turned on. "
        "Every time a config class option is accessed, the config class will be reloaded. "
        "On access config reloading should only be used during testing and debugging. "
        "Do not run with this enabled in production. "
    )


def disable_on_access_config_reloading() -> None:
    ENABLE_ON_ACCESS_CONFIG_RELOADING.unset()
    logging.info("On access config reloading has been turned off.")


# TODO: Add a way to turn this off via env vars. We prolly want to host this in a config class.
if "PYTHON_SDK_CONFIG_ENABLE_ON_ACCESS_CONFIG_RELOADING" in os.environ:
    enable_on_access_config_reloading()
