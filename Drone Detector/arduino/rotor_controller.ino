#include <Arduino.h>

const int STEP_PIN = 2;
const int DIR_PIN = 3;
const int LIMIT_PIN = 7;

const int STEPS_PER_REV = 3200;

long currentStep = 0;
String command = "";


void stepMotor(bool direction, int steps) {
  digitalWrite(DIR_PIN, direction);

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(500);

    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(500);
  }
}


void homeMotor() {
  digitalWrite(DIR_PIN, LOW);

  while (digitalRead(LIMIT_PIN) == HIGH) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(600);

    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(600);
  }

  currentStep = 0;

  Serial.println("HOMED");
}


void moveToAngle(float angle) {
  long targetStep =
    (angle / 360.0) * STEPS_PER_REV;

  long difference =
    targetStep - currentStep;

  if (difference > 0) {
    stepMotor(HIGH, difference);
  }
  else {
    stepMotor(LOW, -difference);
  }

  currentStep = targetStep;

  Serial.println("DONE");
}


void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(LIMIT_PIN, INPUT_PULLUP);

  Serial.begin(115200);
}


void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "HOME") {
      homeMotor();
    }

    if (command.startsWith("GOTO:")) {
      float angle =
        command.substring(5).toFloat();

      moveToAngle(angle);
    }
  }
}
