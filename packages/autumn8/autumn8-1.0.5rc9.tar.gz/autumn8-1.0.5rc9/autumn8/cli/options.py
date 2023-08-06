from typing import List, Literal, Optional, Union

import click
import questionary
from click import ClickException
from questionary import Choice

from autumn8.cli.cli_environment import CliEnvironment
from autumn8.cli.interactive import (
    pick_organization_id,
    verify_organization_id_access,
)
from autumn8.common.config.settings import CloudServiceProvider
from autumn8.common.config.supported_instances import find_instance_config
from autumn8.lib import logging

ENABLE_TOGGLEABLE_ENVIRONMENT = True


def use_environment(func):
    allowed_environments = (
        [env.name for env in CliEnvironment]
        if ENABLE_TOGGLEABLE_ENVIRONMENT
        else [CliEnvironment.PRODUCTION.name]
    )

    return click.option(
        "-e",
        "--environment",
        "--env",
        is_eager=True,  # often used when evaluating other options
        type=click.Choice(allowed_environments, case_sensitive=False),
        default=CliEnvironment.PRODUCTION.name,
        callback=lambda c, p, v: getattr(CliEnvironment, v),
        help="Environment to use",
        hidden=True,
    )(func)


def pick_or_verify_organization(ctx, param, value):
    organization_id = value
    environment = ctx.params["environment"]

    if organization_id is None:
        return pick_organization_id(environment)
    else:
        verify_organization_id_access(environment, organization_id)
        return value


use_organization_id = click.option(
    "-o",
    "--organization_id",
    "--org_id",
    type=int,
    callback=pick_or_verify_organization,
    help="The ID of the Organization to use",
)

use_auto_confirm = click.option(
    "-y",
    "--yes",
    "auto_confirm",
    type=bool,
    is_flag=True,
    help="Skip all confirmation input from the user.",
)

use_quiet_mode = click.option(
    "-q",
    "--quiet",
    is_flag=True,
    callback=lambda ctx, param, value: logging.set_max_log_verbosity(
        logging.ERROR
    )
    if value
    else None,
    help="Skip additional logging, printing only necessary info",
)


def pick_cloud_provider(options: List[CloudServiceProvider]):
    cloud_provider = questionary.select(
        "Choose service provider",
        choices=[
            Choice(title=provider.value, value=provider) for provider in options
        ],
        use_shortcuts=True,
    ).unsafe_ask()
    return cloud_provider


def get_valid_cloud_providers_for_machine_type(
    machine_type,
) -> List[CloudServiceProvider]:
    if machine_type is None:
        return list(CloudServiceProvider)

    instance_config = find_instance_config(
        machine_type, fetch_data_from_cloud_info=False
    )

    valid_providers = [
        instance_config.service_provider,
        CloudServiceProvider.AUTUMN8,
    ]

    return valid_providers


# TODO: update codebase to python 3.12+, unify these two
CloudProviderLabelExtensionsType = Literal[
    "a8f",
    "gcp",
    "aws",
    "None",
]
CloudProviderLabelExtensions: List[str] = [
    "a8f",
    "gcp",
    "aws",
    "None",
]

ExtendedCloudProviderLabel = Union[
    CloudProviderLabelExtensionsType,
    CloudServiceProvider,
]


def map_string_value_to_cloud_provider(
    value: str,
) -> Optional[CloudServiceProvider]:
    if value is None or value == str(None):
        return None

    if value.lower() == "gcp":
        return CloudServiceProvider.GOOGLE

    if value.lower() == "a8f":
        return CloudServiceProvider.AUTUMN8

    if value.lower() == "aws":
        return CloudServiceProvider.AMAZON

    for provider in CloudServiceProvider:
        if provider.value.lower() == value.lower():
            return provider

    raise ClickException(
        f"'{value}' is not a valid cloud provider. It must be one of "
        + f"{CloudProviderLabelExtensions+ [p.value for p in CloudServiceProvider] }",
    )


def get_callback_for_picking_valid_cloud_provider(
    optional: bool = False, default_value: Optional[CloudServiceProvider] = None
):
    def callback(ctx: click.Context, param: click.Parameter, value: str):
        provider_from_value = map_string_value_to_cloud_provider(value)

        machine_type = ctx.params.get("machine_type")
        valid_cloud_providers = get_valid_cloud_providers_for_machine_type(
            machine_type
        )

        if provider_from_value is None:
            if optional:
                return default_value
            return pick_cloud_provider(valid_cloud_providers)

        for provider in valid_cloud_providers:
            if provider is provider_from_value:
                return provider

        raise ClickException(
            f"{provider_from_value} is not a valid cloud provider for machine "
            + f"{machine_type}. It must be one of {valid_cloud_providers}",
        )

    return callback


def use_cloud_provider_picker(
    optional: bool = False, default_value: Optional[CloudServiceProvider] = None
):
    return click.option(
        "-c",
        "--cloud_provider",
        type=click.Choice(
            CloudProviderLabelExtensions
            + [p.value for p in CloudServiceProvider],
            case_sensitive=False,
        ),
        callback=get_callback_for_picking_valid_cloud_provider(
            optional=optional, default_value=default_value
        ),
        help="Cloud provider to use",
    )
