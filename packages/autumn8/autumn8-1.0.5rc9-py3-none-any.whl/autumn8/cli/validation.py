import datetime
import json
import os
from typing import Optional

import jsonschema
import jsonschema.exceptions
import questionary
from jsonschema import validate
from prompt_toolkit.document import Document


class IsoDatetimeValidator(questionary.Validator):
    @classmethod
    def validate_string(cls, maybe_iso_datetime_string: Optional[str]):
        if maybe_iso_datetime_string is None or maybe_iso_datetime_string == "":
            raise questionary.ValidationError(message="Input is empty")

        try:
            date = datetime.datetime.fromisoformat(
                maybe_iso_datetime_string
            ).astimezone()
            if date < datetime.datetime.now().astimezone():
                raise questionary.ValidationError(
                    message="Date/time entered has already passed"
                )

        except ValueError as exc:
            raise questionary.ValidationError(
                message="Input is not a valid ISO format time string"
            ) from exc

    @classmethod
    def is_valid_iso_datetime_string(
        cls, maybe_iso_datetime_string: str
    ) -> bool:
        return cls.get_maybe_error_message(maybe_iso_datetime_string) is None

    @classmethod
    def get_maybe_error_message(
        cls, maybe_iso_datetime_string: str
    ) -> Optional[str]:
        try:
            IsoDatetimeValidator.validate_string(maybe_iso_datetime_string)
            return None
        except questionary.ValidationError as exc:
            return exc.message

    def validate(self, document: Document) -> None:
        IsoDatetimeValidator.validate_string("\n".join(document.lines))


INPUT_DIMS_JSONSCHEMA = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "array",
        "minItems": 1,
        "items": {"type": "number"},
    },
}


def validate_input_dims_json(json_string: str):
    if json_string == "":
        return True

    try:
        json_data = json.loads(json_string)
        validate(instance=json_data, schema=INPUT_DIMS_JSONSCHEMA)
    except (
        jsonschema.exceptions.ValidationError,
        json.decoder.JSONDecodeError,
    ):
        return False
    return True


def validate_input_file(path: str):
    if not os.path.exists(path):
        return False

    if not os.path.isfile(path):
        return False

    try:
        with open(path, "r") as f:
            json_data = json.load(f)

    except json.decoder.JSONDecodeError:
        return False
    return True
