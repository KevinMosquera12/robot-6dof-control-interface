#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  150  // Valor mínimo para el servo
#define SERVOMAX  600  // Valor máximo para el servo

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(50);  // Frecuencia para servos
}

void loop() {
  if (Serial.available()) {
    int id = Serial.read();         // Canal del servo (0 a 5)
    int angle = Serial.read();      // Ángulo del servo (0 a 180)
    int pulse = map(angle, 0, 180, SERVOMIN, SERVOMAX);
    pwm.setPWM(id, 0, pulse);
  }
}
