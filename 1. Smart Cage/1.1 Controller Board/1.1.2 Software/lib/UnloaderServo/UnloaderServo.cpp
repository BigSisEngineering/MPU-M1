#include "UnloaderServo.h"
#include "DebounceInput.h"
#include "Servo.h"

void Unloader::init(uint8_t sensor_pin)
{
  m_sensor_pin = sensor_pin;
  pinMode(m_sensor_pin, INPUT_PULLUP);
}

void Unloader::setServo(Servo *ar_servo)
{
  m_servo = ar_servo;
}

void Unloader::homingBySensor()
{
  if (m_servo == nullptr) return;
  if (!debounceDigitalRead(m_sensor_pin, true)) // Somewhere in the middle
  {
    m_servo->setWheelMode(ID_UNLOADER_MOTOR);            // Speed Mode
    m_servo->moveSpeed(ID_UNLOADER_MOTOR, -1 * 200, 15); // Go backward
    uint32_t timer = millis();
    int8_t   status{ 0 };
    while (status == 0)
    {
      if (debounceDigitalRead(m_sensor_pin, true)) { status = 1; }
      if ((millis() - timer) > (8 * 1000)) { status = -1; }
    }
  }

  m_servo->moveSpeed(ID_UNLOADER_MOTOR, 0, 15);
  // // already retracted && set the count
  m_servo->setServoMode(ID_UNLOADER_MOTOR, false);
  m_servo->setZero(ID_UNLOADER_MOTOR);
  m_retracted_count = COUNT_ZERO;
  m_extended_count  = m_retracted_count + COUNT_UNLOADER_TO_EXTEND;
  m_is_init         = true;
}

ReadBack_Status Unloader::homingByLoad(uint8_t load_threadhold = 150)
{
  if (m_is_error) return ReadBack_Status::ERROR;
  if (m_servo == nullptr) return ReadBack_Status::ERROR;
  m_servo->setWheelMode(ID_UNLOADER_MOTOR); // Speed Mode
  delay(100);
  m_servo->moveSpeed(ID_UNLOADER_MOTOR, 200, 15);
  // TODO 1. Implement message check
  ReadBack_Status res{ ReadBack_Status::IDLE };
  int16_t         load{ 0 };
  while (true)
  {
    res = m_servo->getLoad(ID_UNLOADER_MOTOR, load);
    if (load >= load_threadhold) break;
  }
  /* -------------------------------------------------------------------------------------------- */
  m_servo->stop(ID_UNLOADER_MOTOR);
  m_servo->moveSpeed(ID_UNLOADER_MOTOR, 0, 50);
  m_servo->setServoMode(ID_UNLOADER_MOTOR, false);
  m_servo->setZero(ID_UNLOADER_MOTOR);
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, COUNT_ZERO - 100, 100, 100);
  delay(m_servo->calcDelayTime(100, 100, ST3215_MaxAcc));
  m_servo->setZero(ID_UNLOADER_MOTOR);
  /* -------------------------------------------------------------------------------------------- */
  m_retracted_count = COUNT_ZERO - COUNT_UNLOADER_TO_EXTEND;
  m_extended_count  = COUNT_ZERO;
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, m_retracted_count, 200, ST3215_MaxAcc);
  uint16_t delay_time = m_servo->calcDelayTime(COUNT_UNLOADER_TO_EXTEND, 200, ST3215_MaxAcc);
  res                 = m_servo->delayWithLoadDetection(ID_UNLOADER_MOTOR,
                                                        delay_time,
                                                        160);
  if (res == ReadBack_Status::OVERLOAD) m_is_error = true;
  m_is_init = true;
  return res;
}

ReadBack_Status Unloader::unload()
{
  if (m_is_error) return ReadBack_Status::ERROR;
  if (m_servo == nullptr) return ReadBack_Status::ERROR;
  if (!m_is_init) return ReadBack_Status::NOT_INIT;
  ReadBack_Status res{ ReadBack_Status::NORMAL };
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, m_extended_count, ST3215_MaxSpeed, ST3215_MaxAcc);
  res = m_servo->delayWithLoadDetection(ID_UNLOADER_MOTOR, 1000, 850);
  if (res != ReadBack_Status::NORMAL)
  {
    m_is_error = true;
    return res;
  }
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, m_retracted_count, ST3215_MaxSpeed, ST3215_MaxAcc);
  res = m_servo->delayWithLoadDetection(ID_UNLOADER_MOTOR, 1000, 850);
  if (res != ReadBack_Status::NORMAL)
  {
    m_is_error = true;
    return res;
  }
  return res;
}

void Unloader::resetError() { m_is_error = false; }

bool Unloader::isError() const { return m_is_error; }
