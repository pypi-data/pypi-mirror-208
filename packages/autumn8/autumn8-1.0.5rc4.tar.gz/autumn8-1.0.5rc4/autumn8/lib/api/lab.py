import io
import json
from threading import Lock
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

import appdirs
import boto3
import httpx
import requests
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import PartTypeDef
from mypy_boto3_sts.type_defs import CredentialsTypeDef
from requests.auth import HTTPBasicAuth
from tqdm.contrib.concurrent import thread_map

from autumn8.cli import pending_uploads
from autumn8.cli.analyze import is_model_file_link_external, s3path_join
from autumn8.cli.cli_environment import CliEnvironment
from autumn8.lib import logging
from autumn8.lib.api_creds import retrieve_api_creds
from autumn8.lib.http import require_ok_response, url_with_params

DEFAULT_MAX_UPLOAD_WORKERS = 4

APP_NAME = "autumn8"
APP_AUTHOR = "autumn8"

logger = logging.getLogger(__name__)

data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)


def fetch_user_data(environment: CliEnvironment):
    user_id, api_key = None, None
    autodl_host = environment.value.app_host
    try:
        user_id, api_key = retrieve_api_creds()
    except:
        raise Exception(
            f"API key is missing! To configure API access, please visit {autodl_host}/profile and generate an API key, then run `autumn8-cli login`"
        )

    user_api_route = f"{autodl_host}/api/user"
    response = requests.get(
        user_api_route,
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(user_id, api_key),
    )

    require_ok_response(response)
    return json.loads(response.text)["user"]


def get_model(environment: CliEnvironment, organization_id: int, model_id: int):
    autodl_host = environment.value.app_host
    api_route = f"{autodl_host}/api/lab/model/stub"
    logger.info("Fetching model with id=%s", model_id)
    response = requests.get(
        url_with_params(
            api_route,
            {"organization_id": organization_id, "model_id": model_id},
        ),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
    )

    require_ok_response(response)
    return response.json()


def delete_model(
    environment: CliEnvironment,
    organization_id: int,
    model_id: int,
):
    autodl_host = environment.value.app_host
    api_route = f"{autodl_host}/api/lab/model"
    logger.info("Deleting model with id=%s", model_id)
    response = requests.delete(
        url_with_params(
            api_route,
            {"organization_id": organization_id, "model_id": model_id},
        ),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
    )

    require_ok_response(response)
    return response.json()


def post_model(
    environment: CliEnvironment,
    organization_id: int,
    model_config: Dict[str, Any],
):
    autodl_host = environment.value.app_host
    api_route = f"{autodl_host}/api/lab/model"
    logger.info("Submitting model to %s", api_route)
    response = requests.post(
        url_with_params(api_route, {"organization_id": organization_id}),
        headers={"Content-Type": "application/json"},
        data=json.dumps(model_config),
        auth=HTTPBasicAuth(*retrieve_api_creds()),
    )

    require_ok_response(response)
    return response.json()


FileUploadFileType = Union[Literal["model"], Literal["input"]]


def normal_or_multipart_upload(
    organization_id: int,
    environment: CliEnvironment,
    file: io.BufferedReader,
    file_name: str,
    file_type: FileUploadFileType,
    resume_args,
    id_key,
    mpu_id=None,
    max_upload_workers=DEFAULT_MAX_UPLOAD_WORKERS,
):
    file.seek(0, 2)  # seek to end of file
    total_bytes = file.tell()
    file.seek(0)

    permissions = request_temporary_model_file_upload_permissions(
        environment, organization_id, file_name, file_type
    )

    # AWS dissallow multipart upload of files under 5MB
    if total_bytes < 6 * 1024**2:
        return normal_upload(environment, permissions, file)
    else:
        return multipart_upload(
            environment=environment,
            permissions=permissions,
            file=file,
            resume_args=resume_args,
            id_key=id_key,
            mpu_id=mpu_id,
            max_upload_workers=max_upload_workers,
        )


class FileUploadPermissionsResponse(TypedDict):
    message: str
    object_key: str
    bucket_name: str
    credentials: CredentialsTypeDef


def request_temporary_model_file_upload_permissions(
    environment: CliEnvironment,
    organization_id: int,
    file_name: str,
    file_type: FileUploadFileType,
):
    autodl_host = environment.value.app_host
    api_route = f"{autodl_host}/api/lab/model/upload_sts"
    response = requests.get(
        url_with_params(
            api_route,
            {
                "organization_id": organization_id,
                "file_name": file_name,
                "file_type": file_type,
            },
        ),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(*retrieve_api_creds()),
    )

    require_ok_response(response)
    return FileUploadPermissionsResponse(response.json())


def get_s3_client_from_temporary_permissions(
    environment: CliEnvironment, permissions: FileUploadPermissionsResponse
):
    credentials = permissions["credentials"]
    S3 = boto3.resource(
        "s3",
        endpoint_url=environment.value.s3_host,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    return S3


def normal_upload(
    environment: CliEnvironment,
    permissions: FileUploadPermissionsResponse,
    file,
):
    S3 = get_s3_client_from_temporary_permissions(environment, permissions)

    object_key = permissions["object_key"]
    S3.Bucket(permissions["bucket_name"]).Object(object_key).upload_fileobj(
        file
    )
    return object_key


def get_uploaded_parts(
    s3_client: S3Client, s3_bucket_name, s3_file_url, upload_id
) -> List[PartTypeDef]:
    res = s3_client.list_parts(
        Bucket=s3_bucket_name, Key=s3_file_url, UploadId=upload_id
    )
    return list(res["Parts"]) if "Parts" in res else []


def upload_part(
    part_number,
    s3_client: S3Client,
    s3_bucket_name,
    s3_file_url,
    file,
    part_size_in_bytes,
    total_bytes,
    mpu_id,
    parts_already_uploaded: Dict[int, PartTypeDef],
    lock,
):
    with lock:
        file.seek((part_number - 1) * part_size_in_bytes)
        data = file.read(part_size_in_bytes)

    if not len(data):
        return

    if part_number in parts_already_uploaded:
        part = parts_already_uploaded[part_number]
        # FIXME: these checks are pretty slow, I'm not sure why
        if len(data) != part.get("Size"):
            raise Exception(
                "Upload corrupted: Size mismatch: local "
                + str(len(data))
                + ", remote: "
                + str(part.get("Size"))
            )
        return
    else:
        part = s3_client.upload_part(
            Body=data,
            Bucket=s3_bucket_name,
            Key=s3_file_url,
            UploadId=mpu_id,
            PartNumber=part_number,
        )


def multipart_upload(
    environment: CliEnvironment,
    permissions: FileUploadPermissionsResponse,
    file,
    resume_args,
    id_key,
    mpu_id=None,
    max_upload_workers=DEFAULT_MAX_UPLOAD_WORKERS,
):
    file.seek(0, 2)  # seek to end of file
    total_bytes = file.tell()
    file.seek(0)  # seek to start of file
    # max total upload size is 100GB
    part_size_in_bytes = max(
        10 * 1024**2, total_bytes // 500
    )  # minimum part size on aws is 5MB, list part returns max 1000 parts

    # we have to use low-level API to be able to support
    # resumable uploads - https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpu-upload-object.html
    s3_client = get_s3_client_from_temporary_permissions(
        environment, permissions
    ).meta.client
    s3_bucket_name = permissions["bucket_name"]
    compatible_s3_file_url = permissions["object_key"]

    if mpu_id != None:
        print(f"Resuming upload with id {mpu_id}")
        parts_already_uploaded = {
            part["PartNumber"]: part
            for part in get_uploaded_parts(
                s3_client, s3_bucket_name, compatible_s3_file_url, mpu_id
            )
            if "PartNumber" in part and "Size" in part
        }
    else:
        parts_already_uploaded = {}
        mpu = s3_client.create_multipart_upload(
            Bucket=s3_bucket_name, Key=compatible_s3_file_url
        )
        mpu_id = mpu["UploadId"]
        print(f"Created new multipart upload with id {mpu_id}")

    resume_args[id_key] = mpu_id
    pending_uploads.update_upload(resume_args["run_id"], resume_args)

    # +2, because we assume there's always this final part which is smaller than the rest, and the range end has to be larger by 1 because it's not included
    part_numbers_to_upload = set(
        range(1, (total_bytes - 1) // part_size_in_bytes + 2)
    )
    lock = Lock()
    thread_map(
        lambda part_number: upload_part(
            part_number=part_number,
            s3_client=s3_client,
            s3_bucket_name=s3_bucket_name,
            s3_file_url=compatible_s3_file_url,
            file=file,
            part_size_in_bytes=part_size_in_bytes,
            parts_already_uploaded=parts_already_uploaded,
            total_bytes=total_bytes,
            mpu_id=mpu_id,
            lock=lock,
        ),
        part_numbers_to_upload,
        max_workers=max_upload_workers,
    )

    all_parts = get_uploaded_parts(
        s3_client, s3_bucket_name, compatible_s3_file_url, mpu_id
    )

    s3_client.complete_multipart_upload(
        Bucket=s3_bucket_name,
        Key=compatible_s3_file_url,
        UploadId=mpu_id,
        MultipartUpload={
            "Parts": [  # type: ignore (partial Part type works fine in practice)
                {
                    "PartNumber": part.get("PartNumber"),
                    "ETag": part.get("ETag"),
                }
                for part in all_parts
            ]
        },
    )


# TODO: fix s3 file structure so that this is not needed
def get_hacked_legacy_backwards_compatible_s3_file_url(
    s3_root_folder_name: Optional[str],
    s3_file_url: str,
):
    return s3path_join(s3_root_folder_name or "", s3_file_url)


def post_model_file(
    organization_id: int,
    environment: CliEnvironment,
    filepath_or_url: str,
    file_type: FileUploadFileType,
    resume_args,
    id_key,
    upload_id=None,
    max_upload_workers=DEFAULT_MAX_UPLOAD_WORKERS,
):
    if is_model_file_link_external(filepath_or_url):
        # attaching directly without any reuploads
        return filepath_or_url

    file_name = os.path.basename(filepath_or_url)

    with open(filepath_or_url, "rb") as file:
        return normal_or_multipart_upload(
            organization_id,
            environment=environment,
            file=file,
            file_name=file_name,
            file_type=file_type,
            resume_args=resume_args,
            id_key=id_key,
            mpu_id=upload_id,
            max_upload_workers=max_upload_workers,
        )


def async_prediction(
    environment: CliEnvironment, organization_id: int, model_id: int
):
    autodl_host = environment.value.app_host
    new_url = url_with_params(
        f"{autodl_host}/api/lab/model/async_prediction",
        {
            "model_id": model_id,
            "organization_id": organization_id,
        },
    )
    response = requests.post(
        new_url,
        auth=HTTPBasicAuth(*retrieve_api_creds()),
    )
    require_ok_response(response)
    return response
