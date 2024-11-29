// UnloaderServo.h

#ifndef UNLOADER_SERVO_H
#define UNLOADER_SERVO_H

#include "AnalogSensors.h"
#include "Define.h"
#include <Arduino.h>
#include <TimerOne.h>

class Servo; // Forward declaration of Servo class

class Unloader {
public:
  const uint16_t COUNT_ZERO = 2048;
  const uint16_t COUNT_UNLOADER_TO_EXTEND = 0; // around 120 deg

  // Initialize with just the sensor pin
  void init(); // Removed unnecessary argument for sensor pin

  // Setter for AnalogSensors
  void setSensor(AnalogSensors *sensorObj);

  // Setter for Sensor Pins
  void setSensorPins(uint8_t num_of_sensors, const uint8_t *sensor_pins); // <-- Add this declaration

  // Setter for Servo
  void setServo(Servo *ar_servo);

  // Actions
  ReadBack_Status homing();
  ReadBack_Status unload();
  void resetError();
  int16_t getUnloaderPos();
  ReadBack_Status LoadDetection(const uint8_t &id, uint16_t ms, uint16_t load_limit = NULL);

  // Sense
  bool isError() const;

  // Timer callback function for checking the sensor
  void checkSensor();

  // Static instance pointer for timer interrupt access
  static Unloader *instance;

  volatile bool sensorTriggered{false};

private:
  Servo *m_servo{nullptr};
  bool m_is_init{false};
  bool m_is_error{false};
  uint8_t m_sensor_pin{0};
  int16_t m_retracted_count{0};
  int16_t m_extended_count{0};

  AnalogSensors *m_sensorObj{nullptr}; 
};

#endif