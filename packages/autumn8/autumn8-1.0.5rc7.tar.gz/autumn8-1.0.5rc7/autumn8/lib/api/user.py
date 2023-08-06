import posixpath

import requests
from requests.auth import HTTPBasicAuth

from autumn8.cli.cli_environment import CliEnvironment
from autumn8.lib import logging
from autumn8.lib.api_creds import retrieve_api_creds
from autumn8.lib.http import require_ok_response

logger = logging.getLogger(__name__)


def user_api_url(environment: CliEnvironment, subpath: str) -> str:
    autodl_host = environment.value.app_host
    if subpath:
        return f"{autodl_host}/api/user/{subpath}"
    return f"{autodl_host}/api/user"


def fetch_user_data(environment: CliEnvironment):
    user_id, api_key = retrieve_api_creds()

    response = requests.get(
        user_api_url(environment, ""),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(user_id, api_key),
    )

    require_ok_response(response)
    return response.json()["user"]


def fetch_org_api_keys(environment: CliEnvironment, organization_id: int):
    user_id, api_key = retrieve_api_creds()
    autodl_host = environment.value.app_host

    response = requests.get(
        user_api_url(environment, f"inference_api_keys"),
        params={"organization_id": organization_id},
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(user_id, api_key),
    )
    require_ok_response(response)
    return response.json()["api_keys"]
