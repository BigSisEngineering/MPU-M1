#ifndef UNLOADER_SERVO_H
#define UNLOADER_SERVO_H

#include "Define.h"
#include <Arduino.h>

class Servo;

class Unloader
{
public:
  const uint16_t COUNT_ZERO               = 2048;
  const uint16_t COUNT_UNLOADER_TO_EXTEND = 0; // around 120 deg

  /* ---------------------------------------------------------------------------------------------- */
  void init(uint8_t sensor_pin);
  void setServo(Servo *ar_servo);

  // Actions
  ReadBack_Status            homing();
  // void            homingBySensor();
  // ReadBack_Status homingByLoad(uint8_t load_threadhold = 150);
  ReadBack_Status unload();
  void            resetError();

  // Sense
  bool isError() const;

private:
  Servo  *m_servo{ nullptr };
  bool    m_is_init{ false };
  bool    m_is_error{ false };
  uint8_t m_sensor_pin{ 0 };
  int16_t m_retracted_count{ 0 };
  int16_t m_extended_count{ 0 };
};
#endif
