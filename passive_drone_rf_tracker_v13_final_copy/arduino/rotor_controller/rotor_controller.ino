#include <Arduino.h>

/*
  By Kurt Croker
  Passive SDR RF Tracker - Rotor Controller

  Commands:
    PING
    HOME
    STATUS
    GOTO:90

  Responses:
    PONG
    HOMED:0.00
    ANGLE:90.00
    DONE:90.00
    ERR:<message>
*/
// Wiring
const byte STEP_PIN = 2;
const byte DIR_PIN = 3;
const byte ENABLE_PIN = 4;
const byte LIMIT_PIN = 7;

// Mechanical settings
const long MOTOR_FULL_STEPS_PER_REV = 200;

// configure this to match the driver's microstep jumper configuration
const long MICROSTEPS = 16;

// Motor revolutions per antenna revolution.
// Direct drive = 1.0
const float GEAR_RATIO = 1.0;

const long STEPS_PER_ANTENNA_REV =
    (long)(
        MOTOR_FULL_STEPS_PER_REV
        * MICROSTEPS
        * GEAR_RATIO
    );

// Increase these delays if the motor skips steps.
const unsigned int STEP_HIGH_US = 500;
const unsigned int STEP_LOW_US = 500;

// Homing safety cutoff.
const long MAX_HOME_STEPS =
    STEPS_PER_ANTENNA_REV * 2L;

// State
long currentSteps = 0;
bool isHomed = false;
String inputLine = "";


// Helpers
long normalizeSteps(long steps) {
    long value = steps % STEPS_PER_ANTENNA_REV;

    if (value < 0) {
        value += STEPS_PER_ANTENNA_REV;
    }

    return value;
}


float normalizeAngle(float angle) {
    while (angle >= 360.0) {
        angle -= 360.0;
    }

    while (angle < 0.0) {
        angle += 360.0;
    }

    return angle;
}


long angleToSteps(float angleDegrees) {
    float angle = normalizeAngle(angleDegrees);

    return lround(
        (angle / 360.0)
        * STEPS_PER_ANTENNA_REV
    );
}


float stepsToAngle(long steps) {
    return (
        (float)normalizeSteps(steps)
        / (float)STEPS_PER_ANTENNA_REV
    ) * 360.0;
}


// Motor control
void pulseStep() {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(STEP_HIGH_US);

    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(STEP_LOW_US);
}


void moveSteps(long signedSteps) {
    if (signedSteps == 0) {
        return;
    }

    digitalWrite(
        DIR_PIN,
        signedSteps > 0 ? HIGH : LOW
    );

    long count = labs(signedSteps);

    for (long i = 0; i < count; i++) {
        pulseStep();
    }

    currentSteps = normalizeSteps(
        currentSteps + signedSteps
    );
}


// Homing
void homeRotor() {
    digitalWrite(ENABLE_PIN, LOW);

    // Move toward the normally-open switch.
    // INPUT_PULLUP makes the unpressed state HIGH
    // and pressed state LOW.
    digitalWrite(DIR_PIN, LOW);

    long moved = 0;

    while (
        digitalRead(LIMIT_PIN) == HIGH
        && moved < MAX_HOME_STEPS
    ) {
        pulseStep();
        moved++;
    }

    if (digitalRead(LIMIT_PIN) == HIGH) {
        Serial.println("ERR:HOME_SWITCH_NOT_FOUND");
        return;
    }

    // Back off from the switch.
    digitalWrite(DIR_PIN, HIGH);

    for (int i = 0; i < 60; i++) {
        pulseStep();
    }

    delay(100);

    // Approach again slowly for a zero
    digitalWrite(DIR_PIN, LOW);
    moved = 0;

    while (
        digitalRead(LIMIT_PIN) == HIGH
        && moved < 150
    ) {
        pulseStep();
        delayMicroseconds(1000);
        moved++;
    }

    if (digitalRead(LIMIT_PIN) == HIGH) {
        Serial.println("ERR:HOME_REAPPROACH_FAILED");
        return;
    }

    currentSteps = 0;
    isHomed = true;

    Serial.println("HOMED:0.00");
}


// Move to angle
void gotoAngle(float requestedAngle) {
    if (!isHomed) {
        Serial.println("ERR:NOT_HOMED");
        return;
    }

    float targetAngle = normalizeAngle(
        requestedAngle
    );

    long targetSteps = normalizeSteps(
        angleToSteps(targetAngle)
    );

    long current = normalizeSteps(
        currentSteps
    );

    long difference = targetSteps - current;

    // Shortest circular route.
    if (
        difference
        > STEPS_PER_ANTENNA_REV / 2
    ) {
        difference -= STEPS_PER_ANTENNA_REV;
    }
    else if (
        difference
        < -STEPS_PER_ANTENNA_REV / 2
    ) {
        difference += STEPS_PER_ANTENNA_REV;
    }

    digitalWrite(ENABLE_PIN, LOW);
    moveSteps(difference);

    Serial.print("DONE:");
    Serial.println(
        stepsToAngle(currentSteps),
        2
    );
}


void reportStatus() {
    if (!isHomed) {
        Serial.println("ANGLE:UNKNOWN");
        return;
    }

    Serial.print("ANGLE:");
    Serial.println(
        stepsToAngle(currentSteps),
        2
    );
}


// Serial protocol
void handleCommand(String command) {
    command.trim();

    if (command.equalsIgnoreCase("PING")) {
        Serial.println("PONG");
        return;
    }

    if (command.equalsIgnoreCase("HOME")) {
        homeRotor();
        return;
    }

    if (command.equalsIgnoreCase("STATUS")) {
        reportStatus();
        return;
    }

    if (command.startsWith("GOTO:")) {
        float requestedAngle =
            command.substring(5).toFloat();

        gotoAngle(requestedAngle);
        return;
    }

    Serial.println("ERR:UNKNOWN_COMMAND");
}


// Arduino entry points
void setup() {
    pinMode(STEP_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(ENABLE_PIN, OUTPUT);
    pinMode(LIMIT_PIN, INPUT_PULLUP);

    digitalWrite(STEP_PIN, LOW);

    // A4988/DRV8825 enable is active-low
    digitalWrite(ENABLE_PIN, HIGH);

    Serial.begin(115200);
    delay(500);

    Serial.println("RF_TRACKER_READY");
}


void loop() {
    while (Serial.available() > 0) {
        char character =
            (char)Serial.read();

        if (character == '\n') {
            if (inputLine.length() > 0) {
                handleCommand(inputLine);
                inputLine = "";
            }
        }
        else if (character != '\r') {
            if (inputLine.length() < 80) {
                inputLine += character;
            }
        }
    }
}
