#include <Servo.h>

Servo motor;        // Main controlled servo
Servo spinningServo; // Second continuous servo (always rotating)

const int motorPin = 6;
const int spinningServoPin = 7;  // NEW SERVO PIN
const int timePerStep = 2000;     // Time to move between stops (ms)
int currentStop = 0;

// Limit switch pins
const int limitTopPin = 2;     // Top stop
const int limitBottomPin = 3;  // Bottom stop

void setup() {
  Serial.begin(9600);
  motor.attach(motorPin);
  spinningServo.attach(spinningServoPin);

  pinMode(limitTopPin, INPUT_PULLUP);
  pinMode(limitBottomPin, INPUT_PULLUP);

  stopMotor();

  // Set second servo to rotate continuously at fixed speed
  spinningServo.write(92);  // Adjust if needed; ~98 is slight forward rotation
}

void stopMotor() {
  motor.write(95); // Stop signal for continuous rotation servo
}

bool limitReached(int direction) {
  if (direction == 1 && digitalRead(limitTopPin) == LOW) return true;
  if (direction == -1 && digitalRead(limitBottomPin) == LOW) return true;
  return false;
}

void moveToStop(int from, int to) {
  int steps = abs(to - from);
  if (steps == 0) return;

  int direction = (to > from) ? 1 : -1;
  motor.write(direction == 1 ? 0 : 180); // Set motor direction

  for (int i = 0; i < steps; i++) {
    unsigned long start = millis();
    while (millis() - start < timePerStep) {
      if (limitReached(direction)) {
        stopMotor();
        Serial.println("LIMIT REACHED");
        return;
      }
      delay(10);
    }
  }

  stopMotor();
}

void loop() {
  while (Serial.available()) {
    String command = Serial.readStringUntil('\\n');
    if (command.startsWith("MOVE:")) {
      int fromIndex = command.substring(5, 6).toInt();
      int toIndex = command.substring(7).toInt();
      moveToStop(fromIndex, toIndex);
      currentStop = toIndex;
    }
  }

  delay(100);
}
