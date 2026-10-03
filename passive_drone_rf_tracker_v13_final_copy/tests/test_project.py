from pathlib import Path
import sys
import unittest

project_root = Path(__file__).resolve().parents[1]
python_dir = project_root / "python"
sys.path.insert(0, str(python_dir))

import config
from dsp import (
    angular_distance_deg,
    detection_metrics,
    estimate_bearing,
)
from sdr_device import SimulatedReceiver


class ProjectTests(unittest.TestCase):
    def test_circular_distance(self):
        self.assertAlmostEqual(
            angular_distance_deg(359.0, 1.0),
            2.0,
        )

    def test_known_peak_bearing(self):
        angles = list(range(0, 360, 10))
        powers = [-70.0 for _ in angles]

        powers[6] = -52.0
        powers[7] = -45.0
        powers[8] = -50.0

        bearing = estimate_bearing(
            angles,
            powers,
        )

        self.assertLess(
            angular_distance_deg(bearing, 70.0),
            5.0,
        )

    def test_detection_metric(self):
        powers = [
            -70, -69, -71, -70,
            -50,
            -70, -71, -69,
        ]

        result = detection_metrics(
            powers,
            6.0,
        )

        self.assertTrue(result["detected"])
        self.assertGreater(
            result["prominence_db"],
            6.0,
        )

    def test_simulated_source_bearing(self):
        receiver = SimulatedReceiver(seed=7)

        angles = list(range(0, 360, 10))
        powers = [
            receiver.measure_power_db(angle)
            for angle in angles
        ]

        bearing = estimate_bearing(
            angles,
            powers,
        )

        error = angular_distance_deg(
            bearing,
            config.SIMULATED_SOURCE_BEARING_DEG,
        )

        self.assertLess(error, 8.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
