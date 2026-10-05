SDR Drone / RF Tracker

This is a project I made to use an SDR and Arduino to find what direction an RF signal is coming from.

The antenna is mounted to a stepper motor. The Arduino moves the antenna and Python reads the signal strength from the SDR.

The program checks the signal at different angles and prints the angle with the strongest signal.

Files

main.py
Main Python program.

settings.py
Basic settings like COM port, frequency, and scan angle.

arduino/rotor_controller.ino
Arduino code for moving the stepper motor.

requirements.txt
Python libraries needed.

Hardware

Arduino
RTL-SDR
Stepper motor
Stepper motor driver
Directional antenna
Limit switch

Basic Wiring

Arduino D2 -> stepper driver STEP
Arduino D3 -> stepper driver DIR
Arduino D7 -> limit switch

The stepper motor should use its own power supply through the motor driver.

Do not power the stepper directly from the Arduino.

How It Works

1. Python tells the Arduino to home the antenna.

2. Python tells the Arduino to move to an angle.

3. The Arduino moves the stepper.

4. Python reads samples from the SDR.

5. Python calculates the signal power.

6. The antenna moves to the next angle.

7. At the end, Python prints the angle with the strongest signal.

Install

pip install -r requirements.txt

Find the Arduino COM port and put it in settings.py.

Example:

ARDUINO_PORT = "COM4"

Testing Without Hardware

Run:

python main.py --simulate

The test signal is around 70 degrees.

Running With Hardware

Upload:

arduino/rotor_controller.ino

to the Arduino.

Then run:

python main.py

Notes

The default frequency is 915 MHz.

Change this in settings.py if needed.

This program only measures RF signal strength and direction.

It does not automatically know whether the signal is actually coming from a drone.
