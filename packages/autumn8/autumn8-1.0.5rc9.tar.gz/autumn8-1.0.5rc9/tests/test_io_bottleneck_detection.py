import unittest
from collections import defaultdict
from unittest import mock

from autumn8.common.config.settings import Quantization


class TestDataFileSizeCalculation(unittest.TestCase):
    @mock.patch("os.environ", defaultdict(lambda: "123456"))
    def setUp(self):
        from perf_predictor.io.bottleneck_detection import (
            calculate_data_file_size_in_kb,
        )

        self.calculate_data_file_size_in_kb = calculate_data_file_size_in_kb

    def test_fp32(self):
        self.assertEqual(
            self.calculate_data_file_size_in_kb([2, 3, 4], Quantization.FP32),
            0.096,
        )
        self.assertEqual(
            self.calculate_data_file_size_in_kb(
                [[3, 5, 1], [1, 4, 1]], Quantization.FP32
            ),
            0.076,
        )
        self.assertRaises(
            ValueError,
            self.calculate_data_file_size_in_kb,
            [2, [1, 4]],
            Quantization.FP32,
        )
