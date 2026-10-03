from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
python_dir = project_root / "python"
sys.path.insert(0, str(python_dir))

import config
from arduino_link import ArduinoRotor


def main():
    print(f"Opening Arduino on {config.SERIAL_PORT}...")

    rotor = ArduinoRotor()

    try:
        if rotor.ping():
            print("PASS: Arduino replied PONG.")
        else:
            print("FAIL: Arduino did not reply correctly.")

        print("Status:", rotor.status())

        print()
        print(
            "This diagnostic does NOT home or move the motor. "
            "Run tracker.py when you are ready to test motion."
        )
    finally:
        rotor.close()


if __name__ == "__main__":
    main()
