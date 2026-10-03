#Kurt Croker
#Arduino link

from __future__ import annotations

import time

import config


class ArduinoRotor:
    """
    USB serial interface to the Arduino rotor controller.

    Commands:
        PING
        HOME
        STATUS
        GOTO:<angle>

    Responses:
        PONG
        HOMED:0.00
        ANGLE:<angle>
        DONE:<angle>
    """

    def __init__(self):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError(
                "pyserial is not installed. Run: pip install -r requirements.txt"
            ) from exc

        self.serial = serial.Serial(
            port=config.SERIAL_PORT,
            baudrate=config.BAUD_RATE,
            timeout=0.25,
        )

        # many Arduinos reset when the serial port is opened.
        time.sleep(2.0)

        self._drain_startup_text()

    def _drain_startup_text(self):
        while self.serial.in_waiting:
            self.serial.readline()

    def _command(
        self,
        command: str,
        expected_prefix: str,
    ) -> str:
        self.serial.write(
            (command.strip() + "\n").encode("ascii")
        )
        self.serial.flush()

        deadline = time.time() + config.SERIAL_TIMEOUT_SECONDS
        received = []

        while time.time() < deadline:
            raw = self.serial.readline()

            if not raw:
                continue

            line = raw.decode(
                "ascii",
                errors="replace",
            ).strip()

            if not line:
                continue

            received.append(line)

            if line.startswith("ERR:"):
                raise RuntimeError(f"Arduino reported: {line}")

            if line.startswith(expected_prefix):
                return line

        raise TimeoutError(
            f"Timed out waiting for {expected_prefix!r} "
            f"after sending {command!r}. "
            f"Recent input: {received[-8:]}"
        )

    def ping(self) -> bool:
        return self._command("PING", "PONG") == "PONG"

    def home(self) -> str:
        return self._command("HOME", "HOMED:")

    def goto(self, angle_deg: float) -> str:
        angle = angle_deg % 360.0
        return self._command(
            f"GOTO:{angle:.2f}",
            "DONE:",
        )

    def status(self) -> str:
        return self._command("STATUS", "ANGLE:")

    def close(self):
        if self.serial.is_open:
            self.serial.close()


class SimulatedRotor:
    def ping(self) -> bool:
        return True

    def home(self) -> str:
        print("[SIM] Rotor homed at 0.0 degrees")
        return "HOMED:0.00"

    def goto(self, angle_deg: float) -> str:
        normalized = angle_deg % 360.0
        print(f"[SIM] Antenna -> {normalized:.1f} degrees")
        return f"DONE:{normalized:.2f}"

    def status(self) -> str:
        return "ANGLE:SIMULATED"

    def close(self):
        pass
