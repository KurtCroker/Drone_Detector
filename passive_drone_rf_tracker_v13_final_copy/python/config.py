#Kurt Croker
#Configure settings

"""
Project settings.

This project keeps configuration in Python.
"""

# ----------------------------
# Arduino / serial
# ----------------------------
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
SERIAL_TIMEOUT_SECONDS = 12.0

# ----------------------------
# SDR
# ----------------------------
# Start with a known/legal test signal that your SDR can receive.
TARGET_FREQUENCY_HZ = 915_000_000

# RTL-SDR commonly supports 2.4 MS/s reliably.
SAMPLE_RATE_HZ = 2_400_000

# Tune slightly away from the target so the target does not sit
# directly on the RTL-SDR center/DC artifact.
TUNE_OFFSET_HZ = 250_000

CHANNEL_BANDWIDTH_HZ = 200_000
SDR_GAIN_DB = 35.0

SAMPLES_PER_MEASUREMENT = 131_072
MEASUREMENTS_PER_ANGLE = 2

# ----------------------------
# Scan geometry
# ----------------------------
COARSE_START_DEG = 0.0
COARSE_STOP_DEG = 350.0
COARSE_STEP_DEG = 10.0

FINE_HALF_WIDTH_DEG = 20.0
FINE_STEP_DEG = 2.0

# Time to let the antenna stop vibrating after a move.
SETTLE_TIME_SECONDS = 0.15

# The strongest direction must exceed the scan median by at least
# this amount to count as a directional detection.
DETECTION_PROMINENCE_DB = 6.0

# ----------------------------
# Output
# ----------------------------
CSV_LOG_PATH = "rf_scan_log.csv"
PLOT_PATH = "latest_scan.png"

# ----------------------------
# Simulation
# ----------------------------
SIMULATED_SOURCE_BEARING_DEG = 73.0
SIMULATED_NOISE_STD_DB = 0.7
