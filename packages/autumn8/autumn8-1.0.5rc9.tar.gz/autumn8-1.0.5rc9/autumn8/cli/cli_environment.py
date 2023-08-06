import enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvironmentProperties:
    app_host: str
    s3_host: str
    a8f_host: str
    s3_bucket_name: str
    s3_bucket_root_folder: Optional[str]


# TODO remove - official CLI builds should only point toward production


class CliEnvironment(enum.Enum):
    LOCALHOST = EnvironmentProperties(
        app_host="http://localhost",
        s3_host="http://localhost:4566",
        a8f_host="http://localhost:7250",
        s3_bucket_name="predictor-bucket",
        s3_bucket_root_folder=None,
    )
    STAGING = EnvironmentProperties(
        app_host="http://staging.autumn8.ai",
        s3_host="https://s3-accelerate.amazonaws.com",
        a8f_host="http://autumn8functions.default.aws.staging.autumn8.ai",
        s3_bucket_name="autodl-staging",
        s3_bucket_root_folder="autodl-staging",
    )
    PRODUCTION = EnvironmentProperties(
        app_host="https://autodl.autumn8.ai",
        s3_host="https://s3-accelerate.amazonaws.com",
        a8f_host="https://autumn8functions.default.aws.autumn8.ai",
        s3_bucket_name="autodl-staging",
        s3_bucket_root_folder="autodl-production",
    )
