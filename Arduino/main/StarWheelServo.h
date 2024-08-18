#ifndef STARWHEEL_SERVO_H
#define STARWHEEL_SERVO_H

#include "Define.h"
#include <Arduino.h>

class Servo;
class Valve;

class StarWheelServo
{
public:
  // [Encoder Res] * [Gear ratio] / [No. of slot]
  // [4096]        * [150 / 15]   / [80];
  const uint16_t COUNT_FOR_ONE_SLOT = 512;
  const uint8_t  MAX_STEPS          = 80; // NOTE - Changed to one screw homing
  uint16_t       SENSOR_SLOT_OFFSET{ 0 }; // 250 for flat head screw, 128 for set screw
  /* ---------------------------------------------------------------------------------------------- */
  void           init(uint8_t sensor_pin);
  void           setServo(Servo *ar_servo);
  void           setValve(Valve *ar_valve);

  void setCW();
  void setCCW();
  void setSpeed(uint16_t ar_speed, uint8_t ar_acc);

  ReadBack_Status homing(bool use_constant_blast = true);
  ReadBack_Status moveSteps(int8_t step = 1);
  ReadBack_Status moveStep(uint16_t time_ms);
  ReadBack_Status moveCount(uint16_t count);
  void            spin(int8_t speed);

  int8_t getStepCount() const { return (m_step_counter); }

  bool isNextMoveCauseOverflow(int8_t step);
  bool isInited() const;
  bool isError() const;
  void resetCounter();
  void resetError();

private:
  Servo   *m_servo{ nullptr };
  Valve   *m_valve{ nullptr };
  bool     m_is_init{ false };
  bool     m_is_error{ false };
  int8_t   m_direction{ -1 };
  uint8_t  m_sensor_pin{ 0 };
  int16_t  m_move_counter{ 0 };
  uint16_t m_speed{ 0 };
  uint8_t  m_acc{ 0 };

  int8_t m_step_counter{ 0 };
};
#endif
