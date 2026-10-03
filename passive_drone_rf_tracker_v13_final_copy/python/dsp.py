#Kurt Croker

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


def wrap_angle_deg(angle: float) -> float:
    return angle % 360.0


def angular_distance_deg(a: float, b: float) -> float:
    """Shortest absolute angular distance on a circle."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def channel_power_relative_db(
    samples: np.ndarray,
    sample_rate_hz: float,
    target_offset_hz: float,
    channel_bandwidth_hz: float,
) -> float:
    """
    Measure relative power in a frequency channel using an FFT.

    The result is suitable for comparing antenna directions.
    It is noyt calibrated dBm.
    """
    x = np.asarray(samples, dtype=np.complex128)

    if x.size < 64:
        raise ValueError("At least 64 IQ samples are required.")

    # Remove DC mean.
    x = x - np.mean(x)

    # Hann window reduces spectral leakage.
    window = np.hanning(x.size)
    windowed = x * window

    spectrum = np.fft.fftshift(np.fft.fft(windowed))
    freqs = np.fft.fftshift(
        np.fft.fftfreq(x.size, d=1.0 / sample_rate_hz)
    )

    half_bw = channel_bandwidth_hz / 2.0
    mask = np.abs(freqs - target_offset_hz) <= half_bw

    if not np.any(mask):
        raise ValueError(
            "Configured target channel falls outside the captured bandwidth."
        )

    power = np.sum(np.abs(spectrum[mask]) ** 2)
    normalization = np.sum(window ** 2) * x.size

    relative_power = power / max(normalization, 1e-30)
    relative_power = max(float(relative_power), 1e-30)

    return 10.0 * math.log10(relative_power)


def estimate_bearing(
    angles_deg: Sequence[float],
    powers_db: Sequence[float],
    neighborhood_deg: float = 30.0,
) -> float:
    """
    Estimate a bearing using a circular, linear-power weighted average
    around the strongest measured direction.
    """
    if len(angles_deg) != len(powers_db):
        raise ValueError("angles_deg and powers_db must be the same length.")

    if len(angles_deg) == 0:
        raise ValueError("At least one measurement is required.")

    angles = np.asarray(angles_deg, dtype=float)
    powers = np.asarray(powers_db, dtype=float)

    peak_index = int(np.argmax(powers))
    peak_angle = float(angles[peak_index])
    peak_power_db = float(powers[peak_index])

    use = np.array(
        [
            angular_distance_deg(float(angle), peak_angle) <= neighborhood_deg
            for angle in angles
        ],
        dtype=bool,
    )

    local_angles = angles[use]
    local_powers = powers[use]

    # Convert dB difference to a linear relative-power weight.
    weights = 10.0 ** ((local_powers - peak_power_db) / 10.0)
    weights = np.clip(weights, 1e-12, None)

    radians = np.deg2rad(local_angles)

    x = float(np.sum(weights * np.cos(radians)))
    y = float(np.sum(weights * np.sin(radians)))

    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return wrap_angle_deg(peak_angle)

    return wrap_angle_deg(math.degrees(math.atan2(y, x)))


def detection_metrics(
    powers_db: Sequence[float],
    threshold_db: float,
) -> dict:
    """
    Compare the strongest antenna direction to the median direction.

    This is a directional RF detection metric, not drone identification.
    """
    values = np.asarray(powers_db, dtype=float)

    if values.size == 0:
        raise ValueError("At least one power measurement is required.")

    peak_db = float(np.max(values))
    median_db = float(np.median(values))
    prominence_db = peak_db - median_db

    return {
        "peak_db": peak_db,
        "median_db": median_db,
        "prominence_db": prominence_db,
        "detected": bool(prominence_db >= threshold_db),
    }
