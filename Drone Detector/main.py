import argparse
import math
import random
import time

import numpy as np

import settings


def get_signal_power(samples):
    samples = samples - np.mean(samples)

    window = np.hanning(len(samples))
    fft_data = np.fft.fftshift(
        np.fft.fft(samples * window)
    )

    power = np.mean(np.abs(fft_data) ** 2)

    if power <= 0:
        power = 1e-12

    return 10 * np.log10(power)


class ArduinoMotor:
    def __init__(self):
        import serial

        self.ser = serial.Serial(
            settings.ARDUINO_PORT,
            settings.BAUD_RATE,
            timeout=1
        )

        time.sleep(2)

    def send(self, text):
        self.ser.write((text + "\n").encode())

        while True:
            line = self.ser.readline().decode(errors="ignore").strip()

            if line.startswith("DONE"):
                return

            if line.startswith("HOMED"):
                return

    def home(self):
        self.send("HOME")

    def move_to(self, angle):
        self.send(f"GOTO:{angle}")

    def close(self):
        self.ser.close()


class SDR:
    def __init__(self):
        from rtlsdr import RtlSdr

        self.sdr = RtlSdr()
        self.sdr.sample_rate = settings.SAMPLE_RATE
        self.sdr.center_freq = settings.FREQUENCY
        self.sdr.gain = settings.GAIN

    def read_power(self):
        samples = self.sdr.read_samples(
            settings.SAMPLES
        )

        return get_signal_power(samples)

    def close(self):
        self.sdr.close()


class FakeMotor:
    def home(self):
        print("practice motor homed")

    def move_to(self, angle):
        print(f"moving to {angle} degrees")

    def close(self):
        pass


class FakeSDR:
    def read_power_at(self, angle):
        difference = abs(
            (angle - settings.SIMULATED_SIGNAL_ANGLE + 180)
            % 360 - 180
        )

        signal = 20 * math.exp(
            -0.5 * (difference / 20) ** 2
        )

        noise = random.uniform(-1, 1)

        return -70 + signal + noise

    def close(self):
        pass


def run_real():
    motor = ArduinoMotor()
    sdr = SDR()

    results = []

    try:
        motor.home()

        for angle in range(
            settings.START_ANGLE,
            settings.STOP_ANGLE + 1,
            settings.STEP_ANGLE
        ):
            motor.move_to(angle)
            time.sleep(0.2)

            power = sdr.read_power()

            results.append((angle, power))

            print(
                f"{angle:3d} deg : "
                f"{power:.2f} dB"
            )

    finally:
        motor.close()
        sdr.close()

    return results


def run_simulation():
    motor = FakeMotor()
    sdr = FakeSDR()

    results = []

    motor.home()

    for angle in range(
        settings.START_ANGLE,
        settings.STOP_ANGLE + 1,
        settings.STEP_ANGLE
    ):
        motor.move_to(angle)

        power = sdr.read_power_at(angle)

        results.append((angle, power))

        print(
            f"{angle:3d} deg : "
            f"{power:.2f} dB"
        )

    return results


def find_direction(results):
    best_angle, best_power = max(
        results,
        key=lambda item: item[1]
    )

    print()
    print("Strongest direction:")
    print(f"{best_angle} degrees")
    print(f"{best_power:.2f} dB")

    return best_angle


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--simulate",
        action="store_true"
    )

    args = parser.parse_args()

    if args.simulate:
        results = run_simulation()
    else:
        results = run_real()

    find_direction(results)


if __name__ == "__main__":
    main()
