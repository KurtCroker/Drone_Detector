from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
python_dir = project_root / "python"
sys.path.insert(0, str(python_dir))

import config
from sdr_device import RTLSDRReceiver


def main():
    print("Opening RTL-SDR...")
    print(f"Target frequency: {config.TARGET_FREQUENCY_HZ / 1e6:.3f} MHz")

    receiver = RTLSDRReceiver()

    try:
        for number in range(1, 6):
            power = receiver.measure_power_db()
            print(
                f"Measurement {number}: "
                f"{power:.2f} relative dB"
            )

        print("PASS: SDR returned IQ data and power measurements.")
    finally:
        receiver.close()


if __name__ == "__main__":
    main()
