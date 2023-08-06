from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from autumn8.cli.cli_environment import CliEnvironment
from autumn8.common.config.settings import CloudServiceProvider
from autumn8.common.types import Sla
from autumn8.lib.api_creds import retrieve_api_creds
from autumn8.lib.http import require_ok_response, url_with_params

DEFAULT_API_TIMEOUT = 60


def get_running_deployments(
    organization_id: int,
    environment: CliEnvironment,
    model_id: Optional[int] = None,
    service_provider: Optional[CloudServiceProvider] = None,
):
    autodl_host = environment.value.app_host

    params: Dict[str, Any] = {"organization_id": organization_id}
    if model_id is not None:
        params["model_id"] = model_id
    if service_provider is not None:
        params["service_provider"] = service_provider

    deployments_api_route = f"{autodl_host}/api/cloud/deployments"
    # TODO: wrap the requests library in a custom class to handle common logic like auth and headers for json
    response = requests.get(
        url_with_params(deployments_api_route, params),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
        timeout=DEFAULT_API_TIMEOUT,
    )

    require_ok_response(response)
    return response.json()["deployments"]


def deploy_by_best_sla(
    organization_id: int,
    environment: CliEnvironment,
    model_id: int,
    best_sla: Sla,
    schedule_on: Optional[str],
    deployment_id: Optional[str],
    service_provider: CloudServiceProvider,
):
    autodl_host = environment.value.app_host

    params = {
        "organization_id": organization_id,
        "model_id": model_id,
        "best_sla": best_sla.value,
        "schedule_on": schedule_on,
        "deployment_id": deployment_id,
        "cloud_service_provider": service_provider.value,
    }

    print("sending", params)

    deployments_api_route = f"{autodl_host}/api/cloud/deployments/by_sla"
    response = requests.post(
        url_with_params(deployments_api_route, params),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
        timeout=DEFAULT_API_TIMEOUT,
    )

    require_ok_response(response)
    return response.json()


def deploy(
    organization_id: int,
    environment: CliEnvironment,
    model_id: int,
    machine_type: str,
    schedule_on: Optional[str],
    deployment_id: Optional[str],
    service_provider: CloudServiceProvider,
):
    autodl_host = environment.value.app_host

    params = {
        "organization_id": organization_id,
        "model_id": model_id,
        "machine_type": machine_type,
        "schedule_on": schedule_on,
        "deployment_id": deployment_id,
        "cloud_service_provider": service_provider.value,
    }

    deployments_api_route = f"{autodl_host}/api/cloud/deployments"
    response = requests.post(
        url_with_params(deployments_api_route, params),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
        timeout=DEFAULT_API_TIMEOUT,
    )

    require_ok_response(response)
    return response.json()


def terminate_deployment(
    organization_id: int,
    environment: CliEnvironment,
    deployment_id: str,
    service_provider: CloudServiceProvider,
):
    autodl_host = environment.value.app_host

    params = {
        "organization_id": organization_id,
        "service_provider": service_provider.value,
    }

    deployments_api_route = (
        f"{autodl_host}/api/cloud/deployments/{deployment_id}"
    )
    response = requests.delete(
        url_with_params(deployments_api_route, params),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
        timeout=DEFAULT_API_TIMEOUT,
    )

    require_ok_response(response)
    return response.json()
