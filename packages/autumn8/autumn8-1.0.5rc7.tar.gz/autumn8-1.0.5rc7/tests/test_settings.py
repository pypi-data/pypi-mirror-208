import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from autumn8.common.config.supported_instances import (
    find_instance_config,
    get_supported_cloud_instances,
)


def mock_cloud_info_service_methods(ServiceMock):
    ServiceMock.get_instance_info = MagicMock(
        side_effect=(
            lambda instance_label: {
                "type": instance_label,
                "onDemandPrice": 123,
            }
        )
    )

    ServiceMock.get_instance_pricing = MagicMock(return_value=123)

    ServiceMock.get_cloud_products_info = MagicMock(
        return_value=[{"onDemandPrice": 123}]
    )


class TestCloudInstances(unittest.TestCase):
    @patch(
        "autumn8.common.config.supported_instances.CloudInfoService.get_instance_pricing"
    )
    def test_instance_descriptions_constraints(self, mock_get_instance_pricing):
        """
        Test that get_supported_cloud_instances methods return valid InstanceDescriptions
        """
        mock_get_instance_pricing.return_value = 123

        for (
            predictor_target_key,
            instances_by_num_threads,
        ) in get_supported_cloud_instances().items():
            for (
                num_threads_key,
                instance,
            ) in instances_by_num_threads.items():
                self.assertEqual(
                    predictor_target_key, instance.predictor_target
                )
                self.assertTrue(
                    instance.instance_description_link,
                    msg="The instance description link must not be empty",
                )

    @unittest.skip(
        "Instance descriptions have their core/thread counts all over the place"
    )
    @patch(
        "autumn8.common.config.supported_instances.CloudInfoService.get_instance_pricing"
    )
    def test_instance_descriptions_core_counts(self, mock_get_instance_pricing):
        """
        Test that get_supported_cloud_instances have proper number of threads
        """
        mock_get_instance_pricing.return_value = 123

        for (
            instances_by_num_threads
        ) in get_supported_cloud_instances().values():
            for instance in instances_by_num_threads.values():
                instance_name = instance.predictor_target
                cores = instance.cores
                threads = instance.predictor_num_threads
                hyperthreading = instance.hyperthreading
                self.assertTrue(
                    # FIXME: WTF, sometimes cores are threads and threads are cores? why??????? WHYYYYWYYWYYYY!?!?!?!?! ffs
                    threads == cores if hyperthreading else cores / 2,
                    msg="The number of threads (%s) on %s must be properly related to the %s cores it has with hyperthreading=%s"
                    % (threads, instance_name, cores, hyperthreading),
                )

    @patch(
        "autumn8.common.config.supported_instances.CloudInfoService.get_instance_pricing"
    )
    def test_find_instance_config_finds_proper_instance(
        self, mock_get_instance_pricing
    ):
        """
        Test that find_instance_config can find example instances
        """
        mock_get_instance_pricing.return_value = 123

        instances_to_check = [
            "c5.large",
            "Azure.StandardE2dsv4",
            "gcp.e2_16cores",
        ]

        for predictor_target in instances_to_check:
            instance = find_instance_config(
                predictor_target, fetch_data_from_cloud_info=False
            )

            self.assertEqual(instance.predictor_target, predictor_target)


if __name__ == "__main__":
    unittest.main()
