import enum
from typing import Dict

from autumn8.common.config.settings import CloudServiceProvider

ZoneConfig = Dict[CloudServiceProvider, str]

DEFAULT_CLOUD_ZONES_CONFIG: ZoneConfig = {
    CloudServiceProvider.AMAZON: "us-east-1",
    CloudServiceProvider.GOOGLE: "us-central1",
    CloudServiceProvider.ORACLE: "us-sanjose-1",
    CloudServiceProvider.AZURE: "useast",
}


class Sla(str, enum.Enum):
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST_PERFORMANCE = "cost_performance"
    TOTAL_ENERGY = "total_energy"
    EMISSIONS = "emissions"
