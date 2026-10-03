Passive SDR based drome tracker

The Python program runs on the computer.
The Arduino firmware runs on the Arduino.


PROJECT LAYOUT

passive_drone_rf_tracker/

README.txt
WIRING.txt
requirements.txt

python/
    config.py
    tracker.py
    dsp.py
    sdr_device.py
    arduino_link.py

arduino/
    rotor_controller/
        rotor_controller.ino

diagnostics/
    list_serial_ports.py
    test_arduino_link.py
    test_sdr.py

tests/
    test_project.py


WHAT EACH PART DOES

Python:

config.py
Stores all settings.

tracker.py
Main program. Coordinates the Arduino and SDR, scans the antenna, estimates
bearing, logs results, and creates a polar plot.

dsp.py
FFT/power calculations and bearing estimation.

sdr_device.py
Reads IQ samples from the RTL-SDR. Also contains a simulator.

arduino_link.py
Communicates with the Arduino through USB serial.

Arduino:

rotor_controller.ino
Controls the stepper motor, home switch, and antenna angle.


HOW THE SYSTEM COMMUNICATES

Computer
    |
    |---- USB ---- Arduino ---- motor driver ---- stepper motor
    |
    |---- USB ---- RTL-SDR ---- directional antenna

Python sends commands to the Arduino such as:

PING

Arduino replies:

PONG

Python sends:

GOTO:90

Arduino moves the rotor and replies:

DONE:90.00

Python waits for DONE before collecting the SDR measurement.


#BEFORE USING HARDWARE

1. Read WIRING.txt.

2. Upload:

arduino/rotor_controller/rotor_controller.ino

to the Arduino.

3. Install Python packages:

pip install -r requirements.txt

4. Find your Arduino serial port:

python diagnostics/list_serial_ports.py

5. Edit:

python/config.py

and change:

SERIAL_PORT = "COM4"

to your actual port.


SOFTWARE-ONLY TEST

Run:

python tests/test_project.py

Then run the full simulated tracker:

python python/tracker.py --simulate

The simulated transmitter is at 73 degrees.
The tracker should estimate a bearing close to 73 degrees.


ARDUINO COMMUNICATION TEST

This test will not move the motor.

Run:

python diagnostics/test_arduino_link.py

Expected result:

PASS: Arduino replied PONG.


SDR TEST

Run:

python diagnostics/test_sdr.py

It should print five relative power measurements.


FULL HARDWARE TEST

Make sure the antenna rotor can safely rotate and that the cable has enough
slack.

Then run:

python python/tracker.py

The program will:

1. Ping the Arduino.
2. Home the rotor.
3. Scan 0 to 350 degrees in 10 degree increments.
4. Measure SDR power at each direction.
5. Estimate the strongest bearing.
6. If the peak is strong enough, scan around it again in 2 degree increments.
7. Save a CSV log.
8. Save a polar direction plot.
9. Return the rotor to 0 degrees.


SETTINGS

All settings are in:

python/config.py

Important settings:

SERIAL_PORT = "COM4"

TARGET_FREQUENCY_HZ = 915_000_000

SDR_GAIN_DB = 35.0

COARSE_STEP_DEG = 10.0

FINE_STEP_DEG = 2.0

DETECTION_PROMINENCE_DB = 6.0


MOTOR DRIVER:
DRV8825


The default firmware assumes:

200 full steps per motor revolution
1/16 microstepping
1:1 direct drive

you can change these values on top of rotor_controller.ino if your setup is
different.


OUTPUT FILES

rf_scan_log.csv

Contains:
timestamp
scan type
antenna angle
relative RF power
estimated bearing
peak prominence
detection state

latest_scan.png

Polar plot of signal strength versus antenna direction.


FIRST TEST


Used a known test transmitter or other known RF source at a frequency
your SDR can receive.

Put it at a known bearing.

Run the scan.

Compare:

known bearing
estimated bearing

Repeat at several angles and distances.

That gives actual bearing-error measurements
