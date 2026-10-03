#Kurt Croker

from __future__ import annotations

import math
import random
from typing import Optional

import config
from dsp import angular_distance_deg, channel_power_relative_db


class RTLSDRReceiver:
    """
    RTL-SDR receiver.

    pyrtlsdr is imported only in hardware mode so simulation works
    even when the SDR package is not installed.
    """

    def __init__(self):
        try:
            from rtlsdr import RtlSdr
        except ImportError as exc:
            raise RuntimeError(
                "pyrtlsdr is not installed. Run: pip install -r requirements.txt"
            ) from exc

        self.sdr = RtlSdr()
        self.sdr.sample_rate = config.SAMPLE_RATE_HZ
        self.sdr.center_freq = (
            config.TARGET_FREQUENCY_HZ + config.TUNE_OFFSET_HZ
        )
        self.sdr.gain = config.SDR_GAIN_DB

        # Target appears below tuned center by this offset.
        self.target_offset_hz = -config.TUNE_OFFSET_HZ

        # Throw away one startup capture.
        self.sdr.read_samples(
            min(config.SAMPLES_PER_MEASUREMENT, 32_768)
        )

    def measure_power_db(
        self,
        angle_deg: Optional[float] = None,
    ) -> float:
        samples = self.sdr.read_samples(
            config.SAMPLES_PER_MEASUREMENT
        )

        return channel_power_relative_db(
            samples=samples,
            sample_rate_hz=config.SAMPLE_RATE_HZ,
            target_offset_hz=self.target_offset_hz,
            channel_bandwidth_hz=config.CHANNEL_BANDWIDTH_HZ,
        )

    def close(self):
        self.sdr.close()


class SimulatedReceiver:
    """
    Synthetic directional RF source for software testing.
    """

    def __init__(self, seed: int = 7):
        self.source_bearing_deg = config.SIMULATED_SOURCE_BEARING_DEG
        self.random = random.Random(seed)

    def measure_power_db(
        self,
        angle_deg: Optional[float] = None,
    ) -> float:
        if angle_deg is None:
            angle_deg = 0.0

        distance = angular_distance_deg(
            angle_deg,
            self.source_bearing_deg,
        )

        # Main lobe centered at the simulated transmitter direction.
        main_lobe_db = 22.0 * math.exp(
            -0.5 * (distance / 18.0) ** 2
        )

        # Small rear lobe for a more realistic pattern.
        rear_direction = (
            self.source_bearing_deg + 180.0
        ) % 360.0

        rear_distance = angular_distance_deg(
            angle_deg,
            rear_direction,
        )

        rear_lobe_db = 5.0 * math.exp(
            -0.5 * (rear_distance / 28.0) ** 2
        )

        noise_db = self.random.gauss(
            0.0,
            config.SIMULATED_NOISE_STD_DB,
        )

        return -72.0 + main_lobe_db + rear_lobe_db + noise_db

    def close(self):
        pass
