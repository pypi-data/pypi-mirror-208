import functools
import os
from pathlib import Path

SVC_ROOT = os.environ.get("SVC_ROOT", str(Path.home()) + "/onspecta_svc")


@functools.lru_cache(maxsize=None)
def app():
    class AppEnv:
        NEXT_PUBLIC_AWS_ACCOUNT_ID = os.environ["NEXT_PUBLIC_AWS_ACCOUNT_ID"]

        NEXT_PUBLIC_AWS_S3_HOST_URL = os.environ.get(
            "NEXT_PUBLIC_AWS_S3_HOST_URL"
        )

        NEXT_PUBLIC_AWS_BUCKET_NAME = os.environ["NEXT_PUBLIC_AWS_BUCKET_NAME"]

        # TODO: delete me
        NEXT_PUBLIC_FEATURE_S3_UPLOADS = True

        CONCURRENCY = (
            int(os.environ["CONCURRENCY"])
            if "CONCURRENCY" in os.environ
            else None
        )

        PORT = int(os.environ.get("PORT", 4300))

        DB_URI = os.environ.get("DB_URI")

        DB_USERNAME = os.environ["DB_USERNAME"]
        DB_PASSWORD = os.environ["DB_PASSWORD"]
        DB_ENDPOINT = os.environ["DB_ENDPOINT"]
        DB_PORT = os.environ["DB_PORT"]
        DB_DATABASE = os.environ["DB_DATABASE"]

        MODEL_DEPLOYER_AWS_ACCESS_KEY_ID = os.environ[
            "MODEL_DEPLOYER_AWS_ACCESS_KEY_ID"
        ]
        MODEL_DEPLOYER_AWS_SECRET_KEY = os.environ[
            "MODEL_DEPLOYER_AWS_SECRET_KEY"
        ]

        THIRD_PARTY_CLOUD_CLIENT_AWS_ACCESS_KEY_ID = os.environ.get(
            "THIRD_PARTY_CLOUD_CLIENT_AWS_ACCESS_KEY_ID"
        )
        THIRD_PARTY_CLOUD_CLIENT_AWS_SECRET_KEY = os.environ.get(
            "THIRD_PARTY_CLOUD_CLIENT_AWS_SECRET_KEY"
        )

        CLOUDINFO_API_PATH = os.environ["CLOUDINFO_API_PATH"]

        A8F_PROXY_BILLING_KEY = os.environ.get("A8F_PROXY_BILLING_KEY")

        API_KEYS_BUCKET = os.environ["API_KEYS_BUCKET"]
        API_KEYS_BUCKET_DIRNAME = os.environ.get("API_KEYS_BUCKET_DIRNAME")

        A8F_AWS_BUCKET_S3_HOST_URL = os.environ.get(
            "A8F_AWS_BUCKET_S3_HOST_URL", "https://s3-accelerate.amazonaws.com"
        )

        AUTODL_WORKER_FUNCTION_HOST = os.environ["AUTODL_WORKER_FUNCTION_HOST"]

        K8S_GITLAB_DOCKER_REGISTRY_ACCESS_TOKEN = os.environ.get(
            "K8S_GITLAB_DOCKER_REGISTRY_ACCESS_TOKEN"
        )

        DEPLOYMENTS_PROJECT_NAME = os.environ["DEPLOYMENTS_PROJECT_NAME"]

        AWS_EKS_DEPLOYMENTS_CLUSTER_NAME = os.environ[
            "AWS_EKS_DEPLOYMENTS_CLUSTER_NAME"
        ]
        AWS_EKS_DEPLOYMENTS_CLUSTER_URL = os.environ[
            "AWS_EKS_DEPLOYMENTS_CLUSTER_URL"
        ]
        AWS_EKS_DEPLOYMENTS_CLUSTER_DNS = os.environ[
            "AWS_EKS_DEPLOYMENTS_CLUSTER_DNS"
        ]
        AWS_EKS_IAM_ADMIN_ROLE_ARN = os.environ["AWS_EKS_IAM_ADMIN_ROLE_ARN"]

        GOOGLE_PROJECT_ID = os.environ["GOOGLE_PROJECT_ID"]
        GOOGLE_DEPLOYMENTS_CLUSTER_DNS = os.environ[
            "GOOGLE_DEPLOYMENTS_CLUSTER_DNS"
        ]
        GOOGLE_APPLICATION_CREDENTIALS = os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"
        ]

        SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

        DOCKER_HOST = os.environ.get("DOCKER_HOST")

    return AppEnv


@functools.lru_cache(maxsize=None)
def cli():
    class CliEnv:
        GLOBAL_S3_HOST_URL = os.environ.get(
            "BENCHMARK_AWS_S3_HOST_URL", "https://s3-accelerate.amazonaws.com"
        )

        NEXT_PUBLIC_AWS_ACCESS_KEY_ID = os.environ[
            "NEXT_PUBLIC_AWS_ACCESS_KEY_ID"
        ]
        NEXT_PUBLIC_AWS_SECRET_KEY = os.environ["NEXT_PUBLIC_AWS_SECRET_KEY"]

    return CliEnv


@functools.lru_cache(maxsize=None)
def predictor():
    class PredictorEnv:
        GPU = os.environ["GPU"] == "1"
        TRAINING = os.environ["TRAINING"] == "1"
        MACHINE_ID = os.environ["MACHINE_ID"]
        OMP_NUM_THREADS = int(os.environ["OMP_NUM_THREADS"])
        OVERRIDE_BENCHMARK = os.environ.get("OVERRIDE_BENCHMARK") == "1"
        ARM64 = os.environ["ARM64"] == "1"

        MODELS_PATH = os.environ["MODELS_PATH"]

        TEST = os.environ.get("TEST")

        PREPARATION_MODE = int(os.environ["PREPARATION_MODE"]) == 1

    return PredictorEnv


@functools.lru_cache(maxsize=None)
def worker():
    class WorkerEnv:
        """
        Environment variables accessible both from the main app,
        and from the worker cloud function
        """

        NEXT_PUBLIC_TARGET_ENV_MODE = os.environ["NEXT_PUBLIC_TARGET_ENV_MODE"]

        NEXT_PUBLIC_AUTODL_HOST_DOMAIN = os.environ[
            "NEXT_PUBLIC_AUTODL_HOST_DOMAIN"
        ]

        DATABASE_PATH = os.environ.get(
            "DATABASE_PATH", "perf_predictor/database"
        )

        BENCHMARK_AWS_ACCESS_KEY_ID = os.environ["BENCHMARK_AWS_ACCESS_KEY_ID"]
        BENCHMARK_AWS_SECRET_KEY = os.environ["BENCHMARK_AWS_SECRET_KEY"]
        BENCHMARK_AWS_S3_HOST_URL = os.environ.get(
            "BENCHMARK_AWS_S3_HOST_URL", "https://s3-accelerate.amazonaws.com"
        )

        AUTODL_WORKER_API_TOKEN = os.environ["AUTODL_WORKER_API_TOKEN"]

    return WorkerEnv
