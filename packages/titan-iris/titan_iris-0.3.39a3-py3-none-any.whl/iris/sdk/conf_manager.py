"""This module implements and instantiates the common configuration class used in the project."""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import os
from logging import getLogger
from pathlib import Path
from urllib.parse import urljoin

from omegaconf import DictConfig, OmegaConf

logger = getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                           specifies all modules that shall be loaded and imported into the                           #
#                                current namespace when we use 'from package import *'                                 #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

__all__ = ["ConfManager", "conf_mgr"]


# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                Configuration Manager                                                 #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
def get(
    environment_var: str,
    test_attr: str,
    stag_attr: str,
    prod_attr: str,
    config: DictConfig,
    environment: str,
):
    """Get the value of the environment variable if it exists, else get the value from the config file.

    Helper to get variables from configuration. Environment has priority, then whichever attribute matches the value of
    the environment variable is returned. Default environment is prod.

    Args:
        environment_var (str): environment variable name
        test_attr (str): test attribute name
        stag_attr (str): stag attribute name
        prod_attr (str): prod attribute name
        config (DictConfig): config object
        environment (str): environment name. One of test, stag, prod.

    Returns:
        str: value of the environment variable or config attribute.
        What gets returned depends on the value of the environment variable.
    """
    return os.environ.get(
        environment_var,
        getattr(config, test_attr)
        if "test" in environment.lower()
        else getattr(config, stag_attr)
        if "stag" in environment.lower()
        else getattr(config, prod_attr),
    )


class ConfManager:
    """Configuration Manager class."""

    base_path = Path(__file__).parent.parent
    config = OmegaConf.load(open(base_path / "config.yaml", "r"))
    ENVIRONMENT = os.environ.get("IRIS_ENVIRONMENT", config.environment)

    # get authentication config from config
    AUTH0_CLIENT_ID = get(
        "IRIS_AUTH0_CLIENT_ID",
        "auth0_test_client_id",
        "auth0_stag_client_id",
        "auth0_prod_client_id",
        config,
        ENVIRONMENT,
    )
    AUTH0_DOMAIN = get(
        "IRIS_AUTH0_DOMAIN",
        "auth0_test_domain",
        "auth0_stag_domain",
        "auth0_prod_domain",
        config,
        ENVIRONMENT,
    )

    AUTH0_AUDIENCE = config.auth0_audience
    ALGORITHMS = config.auth0_algorithm
    AUTHENTICATE = config.authenticate
    TELEMETRY = os.environ.get(
        "IRIS_TELEMETRY", config.telemetry
    )  # whether or not to send telemetry data to the server

    CREDENTIALS_PATH = Path.home() / config.keyfile_name
    LOG_LEVEL = os.environ.get("IRIS_LOG_LEVEL", config.log_level)
    # pull the credentials flow from the environment (if it's set, otherwise use the config setting)
    # options are "device" and "client_credentials"
    CREDENTIALS_FLOW = os.environ.get("IRIS_OAUTH_FLOW", config.auth0_flow)

    # base image config from config
    BASE_IMAGE = config.base_image

    base = get("IRIS_BASE", "test_base", "stag_base", "prod_base", config, ENVIRONMENT)

    # pull base url from environment if set, otherwise use the defaults in the config.
    runner_url = urljoin(base, config.runner_path)
    metrics_url = urljoin(base, config.metrics_path)

    # current user, and access token globals.
    # these get set by the flow
    current_user = None
    access_token = None


# ─────────────────────────────────────────────── ConfManager instance ─────────────────────────────────────────────── #


conf_mgr: ConfManager = ConfManager()

debug = os.environ.get("IRIS_DEBUG", "False").lower() in ["t", "true"]
conf_mgr.AUTHENTICATE = False if debug else conf_mgr.AUTHENTICATE
