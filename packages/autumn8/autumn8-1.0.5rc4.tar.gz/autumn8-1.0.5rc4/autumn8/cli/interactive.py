import asyncio
import datetime
import json
import re
from functools import wraps
from typing import Optional, Tuple

import click
import questionary
from questionary import Choice

from autumn8.cli.validation import IsoDatetimeValidator
from autumn8.lib import logging
from autumn8.lib.api.user import fetch_user_data

logger = logging.getLogger(__name__)


def normalize_args(name: str):
    """
    Use this with a click.group to allow both underscores and dashes
    in the CLI flags

    For example, this will make the CLI allow both --model_id and --model-id

    Patch stolen from https://github.com/pallets/click/issues/1123#issuecomment-589989721
    """
    return name.replace("_", "-")


def get_user_organizations(user_data):
    return [mem["organization"] for mem in user_data["memberships"]]


def pick_organization_id(environment):
    user_data = fetch_user_data(environment)
    user_organizations = get_user_organizations(user_data)

    organization_id = questionary.select(
        "Choose organization",
        choices=[
            Choice(title=f"{org['name']} ({org['id']})", value=org["id"])
            for org in user_organizations
        ],
        use_shortcuts=True,
    ).unsafe_ask()
    return organization_id


def verify_organization_id_access(environment, organization_id):
    user_data = fetch_user_data(environment)
    user_organization_ids = [
        org["id"] for org in get_user_organizations(user_data)
    ]
    if organization_id not in user_organization_ids:
        raise Exception(
            f"The user {user_data['email']} does not belong to the organization of id={organization_id}"
        )


def announce_model_upload_response(model_upload_response):
    return announce_json_response({"model_details": model_upload_response})


def announce_json_response(model_upload_response):
    logger.info("")  # newline
    logger.info("Done!")
    click.echo(json.dumps(model_upload_response, indent=4))


def validate_and_ask_about_schedule(
    should_schedule: bool, schedule_on: Optional[str]
) -> Optional[str]:
    if schedule_on is not None:
        try:
            IsoDatetimeValidator.validate_string(schedule_on)
            return schedule_on
        except questionary.ValidationError as exc:
            click.echo(
                f"ERROR: '{schedule_on}' is not a valid date specification"
            )
            click.echo(exc.message + "\n")

    if should_schedule or schedule_on is not None:
        prefill_value = (
            datetime.datetime.now().astimezone().replace(microsecond=0)
            + datetime.timedelta(minutes=5)
        ).isoformat()

        return questionary.text(
            "Pick time to schedule the model to deploy on\n"
            + f"(ie. in 5 minutes it will be '{prefill_value}')\n",
            default=schedule_on or prefill_value,
            validate=IsoDatetimeValidator,
        ).unsafe_ask()

    return None


async def validate_and_ask_about_docker_image_name(docker_image_name: str):
    # https://regex101.com/r/tPWcN4/1
    regex = re.compile(
        r"^(?P<repository>[\w.\-_]+(?:(?::\d+|)(?=/[a-z0-9._-]+/[a-z0-9._-]+))|)(?:/|)(?P<image>[a-z0-9.\-_]+(?:/[a-z0-9.\-_]+|):?[\w.\-_]{1,127})$",
        re.I,
    )
    if not regex.fullmatch(docker_image_name):
        docker_image_name = await questionary.text(
            "Pick docker image to host",
            default=docker_image_name or "",
            validate=lambda input: bool(regex.fullmatch(input)),
        ).unsafe_ask_async()
    final_match = regex.fullmatch(docker_image_name)
    if not final_match:
        raise RuntimeError("Impossible case (?)")
    match_groups: tuple[str] = final_match.groups()

    repository, image = match_groups
    return repository, image


# https://github.com/pallets/click/issues/85
def coro_click_command(func):
    """
    Make a Click command run in an asyncio compatible context

    Breaks synchronous questionary, use async instead
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper
