"""A client service for CloudInfo, reqires CloudInfo to be running and available under CLOUDINFO_API_PATH"""
# https://github.com/banzaicloud/cloudinfo

import os
from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Literal, Optional, Union

import requests
from fastapi import HTTPException

from autumn8.common.config.settings import CloudServiceProvider

CPU_ARCHITECTURE = Literal["x86_64", "arm64"]


@dataclass
class InstanceDescription:
    label: str
    family: str
    instance_description_link: str
    hw: str
    cores: int
    hyperthreading: bool
    usd_per_hr: Optional[float]
    predictor_target: str
    predictor_num_threads: float
    service_provider: CloudServiceProvider
    ram: Optional[float]
    gpuram: Optional[float]
    is_supported_by_a8f: bool = False
    cpu_arch: Optional[CPU_ARCHITECTURE] = None

    # you can determine if the instance is available in govcloud
    # using https://calculator.aws/#/addService/ec2-enhancement
    # and checking either of the GovCloud regions
    aws_govcloud: Union[bool, str] = False


def map_autodl_service_provider_to_cloudinfo_provider(
    autodl_service_provider: str,
) -> str:
    # based off of https://github.com/banzaicloud/cloudinfo/tree/master/internal/cloudinfo/providers
    translation_dict = {
        "Alibaba": "alibaba",
        "Amazon": "amazon",
        "Azure": "azure",
        "DigitalOcean": "digitalocean",
        "Google Cloud Platform": "google",
        "Oracle": "oracle",
    }
    if autodl_service_provider not in translation_dict:
        raise ValueError(
            f"Unsupported service provider {autodl_service_provider}"
        )

    return translation_dict[autodl_service_provider]


class CloudInfoService:
    _cloud_products_info = None

    def __init__(
        self, provider, region, fetch_data_from_cloud_info: bool = True
    ) -> None:
        self.cloudinfo_service_enabled = fetch_data_from_cloud_info
        self.provider = provider
        self.region = region

    @property
    def cloud_products_info(self):
        """Get cloud products info and cache it for further reuse"""

        if not self.cloudinfo_service_enabled:
            return None

        if self._cloud_products_info is None:
            service_type = "compute"
            cloudinfo_api_path = os.environ["CLOUDINFO_API_PATH"]
            provider = map_autodl_service_provider_to_cloudinfo_provider(
                self.provider
            )

            url = f"{cloudinfo_api_path}/providers/{provider}/services/{service_type}/regions/{self.region}/products"

            response = requests.get(
                url,
                headers={"Content-Type": "application/json"},
            )
            if not response.ok:
                if "status not yet cached" in response.text:
                    raise HTTPException(
                        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        detail=f"Try again later, cloudinfo service is still caching machine statuses",
                    )
                raise ValueError(
                    f"Could not get cloud products info from {url}: {response.text}"
                )

            product_descriptions_list = response.json()["products"]

            self._cloud_products_info = {
                product["type"]: product
                for product in product_descriptions_list
            }

        return self._cloud_products_info

    def get_instance_info(self, instance_label):
        if instance_label not in self.cloud_products_info:
            raise (
                ValueError(
                    f"Could not find cloud product of type {instance_label}"
                )
            )
        return self.cloud_products_info[instance_label]

    def get_instance_pricing(self, instance_label):
        if not self.cloudinfo_service_enabled:
            return None

        instance_info = self.get_instance_info(
            instance_label=instance_label,
        )
        return instance_info["onDemandPrice"]

    def build_instance_description(
        self,
        *,
        label: str,
        family: str,
        instance_description_link: str,
        hw: str,
        cores: int,
        hyperthreading: bool,
        hardcoded_usd_per_hr: Optional[float] = None,
        predictor_target: str,
        predictor_num_threads: float,
        ram: float,
        gpuram: Optional[float] = None,
        is_supported_by_a8f: bool = False,
        aws_govcloud: Union[bool, str] = False,
        cpu_arch: Optional[CPU_ARCHITECTURE] = None,
    ) -> InstanceDescription:
        usd_per_hr = (
            hardcoded_usd_per_hr
            if hardcoded_usd_per_hr
            else self.get_instance_pricing(label)
        )

        # TODO rename variables to align with their meaning better
        return InstanceDescription(
            label=label,
            family=family,
            instance_description_link=instance_description_link,
            hw=hw,
            cores=cores,
            hyperthreading=hyperthreading,
            usd_per_hr=usd_per_hr,
            predictor_target=predictor_target,
            predictor_num_threads=predictor_num_threads,
            service_provider=self.provider,
            ram=ram,
            gpuram=gpuram,
            is_supported_by_a8f=is_supported_by_a8f,
            aws_govcloud=aws_govcloud,
            cpu_arch=cpu_arch,
        )

    def build_keyed_instance_description(
        self,
        *,
        label: str,
        family: str,
        instance_description_link: str,
        hw: str,
        cores: int,
        hyperthreading: bool,
        hardcoded_usd_per_hr: Optional[float] = None,
        predictor_target: str,
        predictor_num_threads: int,
        ram: float,
        gpuram: Optional[float] = None,
        is_supported_by_a8f: bool = False,
        aws_govcloud: Union[bool, str] = False,
        cpu_arch: Optional[CPU_ARCHITECTURE] = None,
    ) -> Dict[str, Dict[int, InstanceDescription]]:
        return {
            predictor_target: {
                predictor_num_threads: self.build_instance_description(
                    label=label,
                    family=family,
                    instance_description_link=instance_description_link,
                    hw=hw,
                    cores=cores,
                    hyperthreading=hyperthreading,
                    hardcoded_usd_per_hr=hardcoded_usd_per_hr,
                    predictor_target=predictor_target,
                    predictor_num_threads=predictor_num_threads,
                    ram=ram,
                    gpuram=gpuram,
                    is_supported_by_a8f=is_supported_by_a8f,
                    aws_govcloud=aws_govcloud,
                    cpu_arch=cpu_arch,
                )
            }
        }
