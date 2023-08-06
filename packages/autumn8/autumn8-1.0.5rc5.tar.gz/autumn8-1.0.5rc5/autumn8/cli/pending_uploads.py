import os
import pickle
from pathlib import Path

import appdirs
import click

from autumn8.cli.cli_environment import CliEnvironment

APP_NAME = "autumn8"
APP_AUTHOR = "autumn8"

data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
RESUMABLE_UPLOADS_PATH = os.path.join(data_dir, "uploads.pickle")


def retrieve_pending_uploads():
    if os.path.exists(RESUMABLE_UPLOADS_PATH):
        with open(RESUMABLE_UPLOADS_PATH, "rb") as f:
            return pickle.load(f)

    return {}


def forget_all_pending_uploads():
    os.remove(RESUMABLE_UPLOADS_PATH)


def update_upload(run_id, resume_args):
    if os.path.exists(RESUMABLE_UPLOADS_PATH):
        with open(RESUMABLE_UPLOADS_PATH, "rb") as f:
            data = pickle.load(f)

    else:
        data_path = Path(data_dir)
        data_path.mkdir(parents=True, exist_ok=True)
        data = {}

    data[run_id] = resume_args

    with open(RESUMABLE_UPLOADS_PATH, "wb") as f:
        pickle.dump(data, f)


def abort_and_forget_upload(run_id):
    resume_args = forget_upload(run_id)

    if resume_args is not None:
        environment: CliEnvironment = resume_args["environment"]
        if (
            "model_file_upload_id" in resume_args
            and resume_args["model_file_upload_id"] is not None
        ):
            abort_upload(
                environment,
                resume_args["s3_file_url"],
                resume_args["model_file_upload_id"],
            )

        if (
            "input_file_upload_id" in resume_args
            and resume_args["input_file_upload_id"] is not None
        ):
            abort_upload(
                environment,
                resume_args["s3_file_url"],
                resume_args["input_file_upload_id"],
            )


def forget_upload(run_id):
    if os.path.exists(RESUMABLE_UPLOADS_PATH):
        with open(RESUMABLE_UPLOADS_PATH, "rb") as f:
            data = pickle.load(f)

        if run_id not in data:
            return

        resume_args = data[run_id]

        data.pop(run_id)

        with open(RESUMABLE_UPLOADS_PATH, "wb") as f:
            pickle.dump(data, f)

        return resume_args

    return None


def get_mpu(environment: CliEnvironment, mpu_object_key: str, mpu_id: str):
    raise NotImplementedError()
    s3 = init_s3(environment.value.s3_host)

    s3_bucket_name = environment.value.s3_bucket_name

    mpus = list(
        s3.Bucket(s3_bucket_name).multipart_uploads.filter(
            Prefix=mpu_object_key,
        )
    )

    for m in mpus:
        if m.id == mpu_id:
            return m

    return None


def abort_upload(environment: CliEnvironment, mpu_object_key: str, mpu_id: str):
    # TODO: store permissions locally on the computer for resume, or re-request them for the same file somehow
    # https://gitlab.com/Autumn8Inc/autodl/-/issues/192
    raise NotImplementedError()
    mpu = get_mpu(environment, mpu_object_key, mpu_id)
    if mpu is None:
        click.echo(
            "The upload could not be found on S3. It may have already been aborted or completed."
        )
        return

    s3_bucket_name = environment.value.s3_bucket_name

    s3 = init_s3_client(environment.value.s3_host)

    s3.abort_multipart_upload(
        Bucket=s3_bucket_name, Key=mpu_object_key, UploadId=mpu_id
    )
