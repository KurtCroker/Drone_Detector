#SDR Drone Detector and Tracker

This is a project I’m working on to detect and track RF signals using an SDR and a directional antenna. The main idea is to rotate the antenna, measure signal strength at different angles, and estimate what direction the strongest signal is coming from.

I’m using Python for the SDR signal processing and an Arduino to control the antenna rotation.

How It Works

The system is split into two main parts.

The computer controls the SDR and processes the RF signal using Python. The Arduino controls a stepper motor that rotates the directional antenna.

The basic process is:

1. Python tells the Arduino what angle to move the antenna to.
2. The Arduino rotates the antenna using a stepper motor.
3. The Arduino tells Python when it reaches the angle.
4. The SDR collects IQ samples.
5. Python uses an FFT to measure the signal strength around the selected frequency.
6. The process repeats at different angles.
7. Python compares the measurements and estimates the direction the RF signal is coming from.

The system first performs a larger scan and then performs a smaller scan around the strongest direction to get a more accurate bearing.

#Hardware

Nooelec NESDR SMArt v5
Arduino Uno/Nano
NEMA 17 stepper motor
A4988 stepper motor driver
Directional antenna
Limit switch for homing
External stepper motor power supply
Laptop running Python

#Software

Python
Arduino C/C++
NumPy
PySerial
pyrtlsdr
Matplotlib

Python handles most of the signal processing because it is easier to work with SDR data, FFTs, plotting, and data collection.

The Arduino is mainly used for controlling the stepper motor and keeping track of the antenna position.

#Project Structure

drone_rf_tracker/

config.json
requirements.txt

host/
tracker.py
receiver.py
rotor.py
signal_processing.py

arduino/
rotor_controller/
rotor_controller.ino

tests/
test_bearing.py

Arduino Communication

The computer communicates with the Arduino through USB serial.

For example, Python can send:

GOTO:90

The Arduino rotates the antenna to 90 degrees and responds with:

DONE:90.00

Python waits for this response before taking an SDR measurement so the antenna is not moving while data is being collected.

#Signal Processing

The SDR produces IQ samples.

Python performs an FFT on the samples to convert the data from the time domain into the frequency domain.

The program then measures the relative signal power around the selected frequency.

Example:

Angle    Signal Strength

0 degrees     -71 dB
30 degrees    -68 dB
60 degrees    -54 dB
70 degrees    -45 dB
80 degrees    -48 dB
90 degrees    -57 dB

In this example the strongest signal is coming from around 70 degrees.

The program also uses nearby measurements around the strongest signal to calculate a more accurate estimated bearing.

#Running the Project

Install the Python dependencies:

pip install -r requirements.txt

The program can be tested without the SDR or Arduino using the built-in simulation:

python host/tracker.py --simulate

The simulation creates a fake RF source so the direction-finding code can be tested before connecting the hardware.

To use the real hardware, change the Arduino COM port in config.json.

Example:

"serial_port": "COM4"

The Arduino COM port can be found in the Arduino IDE under:

Tools > Port

Then run:

python host/tracker.py

Current Limitations

The NESDR Smart v5 does not cover the common 2.4 GHz and 5 GHz frequency ranges.

Because of this, the current version is mainly being used to develop and test the direction-finding system, antenna rotation, signal processing, and tracking algorithms.

The current system detects RF energy on a selected frequency. It does not automatically identify every detected RF signal as a drone.

Future Plans

SDR hardware capable of receiving 2.4 GHz and 5 GHz
2.4 GHz and 5 GHz directional antennas
Remote ID detection
Live tracking instead of individual scans
Compass/IMU for absolute heading
Better antenna mount and enclosure
Multiple receiving stations for triangulation
Testing at different distances and angles
Calculating average bearing error
GUI for signal strength and direction

Goal

The main goal of this project is to combine RF, SDR signal processing, embedded systems, programming, and mechanical design into one system.

I also want to collect actual test data and measure how accurate the direction-finding system is instead of only showing that it works.
