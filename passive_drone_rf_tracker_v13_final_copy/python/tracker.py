#Kurt Croker

from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import config
from arduino_link import ArduinoRotor, SimulatedRotor
from dsp import detection_metrics, estimate_bearing, wrap_angle_deg
from sdr_device import RTLSDRReceiver, SimulatedReceiver


def make_coarse_angles() -> list[float]:
    return [
        float(x)
        for x in np.arange(
            config.COARSE_START_DEG,
            config.COARSE_STOP_DEG + 0.001,
            config.COARSE_STEP_DEG,
        )
    ]


def make_fine_angles(center_deg: float) -> list[float]:
    count = int(
        round(
            (2.0 * config.FINE_HALF_WIDTH_DEG)
            / config.FINE_STEP_DEG
        )
    )

    raw = [
        wrap_angle_deg(
            center_deg
            - config.FINE_HALF_WIDTH_DEG
            + i * config.FINE_STEP_DEG
        )
        for i in range(count + 1)
    ]

    result = []
    seen = set()

    for angle in raw:
        key = round(angle, 6)

        if key not in seen:
            seen.add(key)
            result.append(angle)

    return result


def measure_angle(receiver, rotor, angle_deg: float) -> float:
    rotor.goto(angle_deg)
    time.sleep(config.SETTLE_TIME_SECONDS)

    readings = [
        receiver.measure_power_db(angle_deg)
        for _ in range(config.MEASUREMENTS_PER_ANGLE)
    ]

    # Median is more resistant to one bad/noisy capture.
    return float(np.median(readings))


def run_scan(receiver, rotor, angles, label: str):
    powers = []

    print()
    print(f"{label} SCAN - {len(angles)} positions")

    for index, angle in enumerate(angles, start=1):
        power_db = measure_angle(receiver, rotor, angle)
        powers.append(power_db)

        print(
            f"[{index:02d}/{len(angles):02d}] "
            f"{angle:7.2f} deg  "
            f"{power_db:8.2f} relative dB"
        )

    return powers


def print_result(label: str, bearing_deg: float, metrics: dict):
    print()
    print(label)
    print(f"Estimated bearing: {bearing_deg:.1f} degrees")
    print(f"Peak power:        {metrics['peak_db']:.1f} relative dB")
    print(f"Median power:      {metrics['median_db']:.1f} relative dB")
    print(f"Peak prominence:   {metrics['prominence_db']:.1f} dB")
    print(f"Detected:          {metrics['detected']}")


def append_csv(
    scan_type: str,
    angles,
    powers,
    bearing_deg: float,
    metrics: dict,
):
    path = Path(config.CSV_LOG_PATH)
    new_file = not path.exists()

    with path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        fields = [
            "timestamp_utc",
            "scan_type",
            "angle_deg",
            "relative_power_db",
            "estimated_bearing_deg",
            "prominence_db",
            "detected",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        if new_file:
            writer.writeheader()

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        for angle, power in zip(angles, powers):
            writer.writerow(
                {
                    "timestamp_utc": timestamp,
                    "scan_type": scan_type,
                    "angle_deg": f"{angle:.3f}",
                    "relative_power_db": f"{power:.3f}",
                    "estimated_bearing_deg": f"{bearing_deg:.3f}",
                    "prominence_db": f"{metrics['prominence_db']:.3f}",
                    "detected": metrics["detected"],
                }
            )


def save_polar_plot(angles, powers, bearing_deg: float):
    # Lazy import so non-plot diagnostics can run without matplotlib.
    import matplotlib.pyplot as plt

    angles_rad = np.deg2rad(
        np.asarray(angles, dtype=float)
    )

    powers_np = np.asarray(
        powers,
        dtype=float,
    )

    # Matplotlib polar radius is easiest to read with positive values.
    radius = powers_np - np.min(powers_np) + 1.0

    figure = plt.figure(figsize=(8, 8))
    axis = figure.add_subplot(111, projection="polar")

    axis.plot(
        angles_rad,
        radius,
        marker="o",
    )

    axis.scatter(
        [np.deg2rad(bearing_deg)],
        [np.max(radius)],
        s=80,
    )

    axis.set_theta_zero_location("N")
    axis.set_theta_direction(-1)
    axis.set_title(
        "RF Direction Scan\n"
        f"Estimated bearing: {bearing_deg:.1f} degrees"
    )

    figure.tight_layout()
    figure.savefig(
        config.PLOT_PATH,
        dpi=160,
    )

    plt.close(figure)


def create_devices(simulate: bool):
    if simulate:
        return SimulatedReceiver(), SimulatedRotor()

    return RTLSDRReceiver(), ArduinoRotor()


def main():
    parser = argparse.ArgumentParser(
        description="Passive SDR RF direction tracker"
    )

    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Use simulated SDR and rotor instead of real hardware.",
    )

    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Do not create the PNG polar plot.",
    )

    args = parser.parse_args()

    receiver, rotor = create_devices(args.simulate)

    try:
        if not rotor.ping():
            raise RuntimeError("Arduino communication test failed.")

        rotor.home()

        coarse_angles = make_coarse_angles()

        coarse_powers = run_scan(
            receiver,
            rotor,
            coarse_angles,
            "COARSE",
        )

        coarse_metrics = detection_metrics(
            coarse_powers,
            config.DETECTION_PROMINENCE_DB,
        )

        coarse_bearing = estimate_bearing(
            coarse_angles,
            coarse_powers,
        )

        print_result(
            "COARSE RESULT",
            coarse_bearing,
            coarse_metrics,
        )

        final_angles = coarse_angles
        final_powers = coarse_powers
        final_bearing = coarse_bearing
        final_metrics = coarse_metrics
        scan_type = "coarse"

        if coarse_metrics["detected"]:
            fine_angles = make_fine_angles(
                coarse_bearing
            )

            fine_powers = run_scan(
                receiver,
                rotor,
                fine_angles,
                "FINE",
            )

            fine_metrics = detection_metrics(
                fine_powers,
                config.DETECTION_PROMINENCE_DB / 2.0,
            )

            fine_bearing = estimate_bearing(
                fine_angles,
                fine_powers,
                neighborhood_deg=max(
                    6.0,
                    config.FINE_HALF_WIDTH_DEG,
                ),
            )

            final_angles = fine_angles
            final_powers = fine_powers
            final_bearing = fine_bearing
            final_metrics = fine_metrics
            scan_type = "fine"

            print_result(
                "FINAL RESULT",
                fine_bearing,
                fine_metrics,
            )
        else:
            print()
            print(
                "No strong directional peak was found. "
                "Fine scan skipped."
            )

        append_csv(
            scan_type,
            final_angles,
            final_powers,
            final_bearing,
            final_metrics,
        )

        if not args.no_plot:
            save_polar_plot(
                final_angles,
                final_powers,
                final_bearing,
            )

        print()
        print(f"CSV log: {config.CSV_LOG_PATH}")

        if not args.no_plot:
            print(f"Plot:    {config.PLOT_PATH}")

        # Return rotor to home direction to reduce cable winding.
        rotor.goto(0.0)

    finally:
        receiver.close()
        rotor.close()


if __name__ == "__main__":
    main()
