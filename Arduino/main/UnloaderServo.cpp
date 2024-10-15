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

// void Unloader::homingBySensor()
// {
//   if (m_servo == nullptr) return;
//   if (!debounceDigitalRead(m_sensor_pin, true)) // Somewhere in the middle
//   {
//     m_servo->setWheelMode(ID_UNLOADER_MOTOR);            // Speed Mode
//     m_servo->moveSpeed(ID_UNLOADER_MOTOR, -1 * 200, 15); // Go backward
//     uint32_t timer = millis();
//     int8_t   status{ 0 };
//     while (status == 0)
//     {
//       if (debounceDigitalRead(m_sensor_pin, true)) { status = 1; }
//       if ((millis() - timer) > (8 * 1000)) { status = -1; }
//     }
//   }

//   m_servo->moveSpeed(ID_UNLOADER_MOTOR, 0, 15);
//   // // already retracted && set the count
//   m_servo->setServoMode(ID_UNLOADER_MOTOR, false);
//   m_servo->setZero(ID_UNLOADER_MOTOR);
//   m_retracted_count = COUNT_ZERO;
//   m_extended_count  = m_retracted_count + COUNT_UNLOADER_TO_EXTEND;
//   m_is_init         = true;
// }

ReadBack_Status Unloader::homing()
{
  ReadBack_Status res;
  if (m_is_error)
    return ReadBack_Status::ERROR;
  if (m_servo == nullptr)
    return ReadBack_Status::NO_SERIAL;
  if (!m_is_init)
  {
    m_retracted_count = 0;
  }
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, m_retracted_count, ST3215_MaxSpeed, ST3215_MaxAcc);
  uint16_t delayTime = m_servo->calcDelayTime(abs(m_retracted_count - COUNT_ZERO), ST3215_MaxSpeed, ST3215_MaxAcc);
  delay(delayTime + 20); // Adding an extra 20 milliseconds as a buffer

  // TODO perform checks to ensure it reached the desired position
  // m_is_init = true;  // Mark as initialized after successful homing
  // return ReadBack_Status::NORMAL;
  res = m_servo->delayWithLoadDetection(ID_UNLOADER_MOTOR,
                                        delayTime,
                                        1000);
  if (res == ReadBack_Status::OVERLOAD)
  {
    m_is_error = true;
    //    m_is_init = false;
  }
  else
  {
    //    m_is_error = false;
    m_is_init = true;
  }
  return res;
}

// ReadBack_Status Unloader::unload() {
//   if (m_is_error) return ReadBack_Status::ERROR;
//   if (m_servo == nullptr) return ReadBack_Status::NO_SERIAL;
//   if (!m_is_init) return ReadBack_Status::NOT_INIT;

//   const int positionTolerance = 50;  // Tolerance for position checking
//   int16_t currentPosition = 0;       // Variable to hold the current position
//   int16_t targetPosition = 0;        // Variable to hold the target position

//   // Get the current position
//   if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
//     Serial.println("Error reading current position.");
//     return ReadBack_Status::ERROR;  // Return on failure to read position
//   }

//   // Determine target position based on current position
//   if (currentPosition >= 0 && currentPosition <= 370) {
//     targetPosition = 3755;
//   } else if (currentPosition >= 3725 && currentPosition <= 3785) {
//     targetPosition = 341;
//   } else {
//     Serial.println("Invalid current position.");
//     return ReadBack_Status::ERROR;
//   }

//   // Move the servo to the target position
//   m_servo->goPosByCount(ID_UNLOADER_MOTOR, targetPosition, ST3215_MaxSpeed, ST3215_MaxAcc);

//   // Wait until the servo reaches the target position within tolerance
//   // do {
//   //     delay(100); // Brief delay to prevent flooding the servo with requests
//   //     if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
//   //         Serial.println("Error reading position after moving to target position.");
//   //         return ReadBack_Status::ERROR; // Return on failure to read position
//   //     }
//   // } while (!(abs(currentPosition - targetPosition) <= positionTolerance));
//   delay(1500);
//   return ReadBack_Status::NORMAL;
// }

ReadBack_Status Unloader::unload()
{
  ReadBack_Status res;
  if (m_is_error)
    return ReadBack_Status::ERROR;
  if (m_servo == nullptr)
    return ReadBack_Status::NO_SERIAL;
  if (!m_is_init)
    return ReadBack_Status::NOT_INIT;
    
  int16_t currentPosition = 0;
  int16_t targetPosition = 0;
  if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL)
  {
    return ReadBack_Status::ERROR;
  }
  if (currentPosition >= 0 && currentPosition <= 370)
  {
    targetPosition = 3755;
  }
  else if (currentPosition >= 3725 && currentPosition <= 4095)
  {
    targetPosition = 341;
  }
  else
  {
    return ReadBack_Status::ERROR;
  }
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, targetPosition, ST3215_MaxSpeed, ST3215_MaxAcc);
  uint16_t delayTime = m_servo->calcDelayTime(abs(targetPosition - currentPosition), ST3215_MaxSpeed, ST3215_MaxAcc);
  res = m_servo->delayWithLoadDetection(ID_UNLOADER_MOTOR, delayTime, 1000);
  if (res == ReadBack_Status::OVERLOAD)
  {
    m_is_error = true;
    return res;
  }
  return ReadBack_Status::NORMAL;
}


int16_t Unloader::getUnloaderPos()
{
  int16_t currentPosition = 0;
  ReadBack_Status rbs;
  rbs = m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition);
  return currentPosition;
}


void Unloader::resetError()
{
  m_is_error = false;
}


bool Unloader::isError() const
{
  return m_is_error;
}
