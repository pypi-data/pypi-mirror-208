import configparser
import os
from pathlib import Path

import appdirs

from autumn8.exceptions import UserActionRequiredException

APP_NAME = "autumn8"
APP_AUTHOR = "autumn8"


def store_api_creds(user_id, api_key):
    app_config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
    app_config_path = os.path.join(app_config_dir, "autumn8.ini")
    print(f"Saving configuration under {app_config_path}")

    config = configparser.ConfigParser()
    config.read([app_config_path])
    if not config.has_section("api_access"):
        config.add_section("api_access")
    config.set("api_access", "user_id", user_id)
    config.set("api_access", "api_key", api_key)

    path = Path(app_config_dir)
    path.mkdir(parents=True, exist_ok=True)
    file = open(app_config_path, "w")
    config.write(file)


def retrieve_api_creds():
    try:
        app_config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
        app_config_path = os.path.join(app_config_dir, "autumn8.ini")
        config = configparser.ConfigParser()
        config.read(app_config_path)
        if not config.has_section("api_access"):
            config.add_section("api_access")

        user_id = config.get("api_access", "user_id")
        api_key = config.get("api_access", "api_key")
        return user_id, api_key
    # TODO: pick a more specific set of exceptions here
    except Exception as exc:
        raise UserActionRequiredException(
            f"API key is missing! To configure API access, please visit your profile page and generate an API key, then run `autumn8-cli login`"
        ) from exc
