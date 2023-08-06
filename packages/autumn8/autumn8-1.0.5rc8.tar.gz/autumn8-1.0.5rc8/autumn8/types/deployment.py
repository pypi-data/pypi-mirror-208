import enum
from typing import Union

from pydantic import BaseModel


class DeploymentStatus(str, enum.Enum):
    STARTING = "STARTING"
    READY = "READY"
    INVALID = "INVALID"
    CRASHED = "CRASHED"
    SLEEPING = "SLEEPING"
    TERMINATED = "TERMINATED"


class ServerType(str, enum.Enum):
    MULTIMODEL_SERVER = "MULTIMODEL_SERVER"
    CUSTOM_PYTORCH_INFERER = "PYTORCH"  # for CLI imported models
    TORCHSERVE = "TORCHSERVE"
    TENSORFLOW_SERVING = "TENSORFLOW"


class DeploymentView(BaseModel):
    initialization_progress: int = 100
    """Percents of progress, in range from 0 to 100"""
    initialization_status_details: str = (
        "Deployment set up and accepting requests"
    )

    deployment_id: str
    """Unique identifier of the deployment"""
    model_id: int
    """Unique identifier of the model that's hosted by the deployment"""
    instance_type: str

    status: DeploymentStatus = DeploymentStatus.STARTING
    created_at: Union[int, None] = None
    public_dns: Union[str, None] = None
    server_type: Union[ServerType, None] = None
    service_provider: str = "autumn8"
