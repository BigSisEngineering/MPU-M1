#include "UnloaderServo.h"
#include "DebounceInput.h"
#include "Servo.h"

void Unloader::init(uint8_t sensor_pin) {
  m_sensor_pin = sensor_pin;
  pinMode(m_sensor_pin, INPUT_PULLUP);
}

void Unloader::setServo(Servo *ar_servo) {
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

ReadBack_Status Unloader::homing() {
  if (m_is_error) return ReadBack_Status::ERROR;
  if (m_servo == nullptr) return ReadBack_Status::NO_SERIAL;
  if (!m_is_init) {
    m_retracted_count = 0;
  }
  // Simply move the servo to the retracted position at a specified speed and acceleration
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, m_retracted_count, ST3215_MaxSpeed, ST3215_MaxAcc);
  uint16_t delayTime = m_servo->calcDelayTime(abs(m_retracted_count - COUNT_ZERO), ST3215_MaxSpeed, ST3215_MaxAcc);
  delay(delayTime + 20);  // Adding an extra 20 milliseconds as a buffer

  // TODO perform checks to ensure it reached the desired position
  m_is_init = true;  // Mark as initialized after successful homing
  return ReadBack_Status::NORMAL;
}







// ReadBack_Status Unloader::unload() {
//     if (m_is_error) return ReadBack_Status::ERROR;
//     if (m_servo == nullptr) return ReadBack_Status::ERROR;
//     if (!m_is_init) return ReadBack_Status::NOT_INIT;

//     // Directly move the servo to the unload position and wait for completion
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, 1, ST3215_MaxSpeed, ST3215_MaxAcc);
//     // Calculate the delay time needed for the move to complete and then wait
//     uint16_t delayTime = m_servo->calcDelayTime(COUNT_ZERO, ST3215_MaxSpeed, ST3215_MaxAcc) + 50; // Additional buffer time
//     Serial.println(delayTime);
//     delay(delayTime );


//     // Move the servo back to its original position and wait again
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, 2048, ST3215_MaxSpeed, ST3215_MaxAcc);
//     delayTime = m_servo->calcDelayTime(COUNT_ZERO, ST3215_MaxSpeed, ST3215_MaxAcc) + 50; // Recalculate and buffer
//     Serial.println(delayTime);
//     delay(delayTime );

//     return ReadBack_Status::NORMAL;
// }


// ReadBack_Status Unloader::unload() {
//     if (m_is_error) return ReadBack_Status::ERROR;
//     if (m_servo == nullptr) return ReadBack_Status::ERROR;
//     if (!m_is_init) return ReadBack_Status::NOT_INIT;

//     int16_t currentPosition = 0; // Variable to hold the current position
//     ReadBack_Status status;

//     // Move the servo to the unload position and wait for completion
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, 1, ST3215_MaxSpeed, ST3215_MaxAcc);
//     uint16_t delayTime = m_servo->calcDelayTime(COUNT_ZERO, ST3215_MaxSpeed, ST3215_MaxAcc) + 50; // Additional buffer time
//     delay(delayTime);

//     // Get the position after the move
//     status = m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition);
//     Serial.print("Position after moving to 1: ");
//     Serial.println(currentPosition);
//     if (status != ReadBack_Status::NORMAL) {
//         Serial.println("Error reading position after first move.");
//         return status; // Return if there was an error reading the position
//     }

//     // Move the servo back to its original position and wait again
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, 2048, ST3215_MaxSpeed, ST3215_MaxAcc);
//     delayTime = m_servo->calcDelayTime(2048, ST3215_MaxSpeed, ST3215_MaxAcc) + 50; // Recalculate and buffer
//     delay(delayTime);

//     // Get the position after moving back
//     status = m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition);
//     Serial.print("Position after moving back to 2048: ");
//     Serial.println(currentPosition);
//     if (status != ReadBack_Status::NORMAL) {
//         Serial.println("Error reading position after second move.");
//         return status; // Return if there was an error reading the position
//     }

//     return ReadBack_Status::NORMAL;
// }


// ReadBack_Status Unloader::unload() {
//     if (m_is_error) return ReadBack_Status::ERROR;
//     if (m_servo == nullptr) return ReadBack_Status::NO_SERIAL;
//     if (!m_is_init) return ReadBack_Status::NOT_INIT;

//     const int positionTolerance = 50; // Tolerance for position checking
//     int16_t currentPosition = 0; // Variable to hold the current position

//     // Target positions
//     int16_t firstTargetPosition = 1;
//     int16_t secondTargetPosition = 2047;

//     // Function to check if current position is within tolerance of target position
//     auto isWithinTolerance = [positionTolerance](int16_t currentPosition, int16_t targetPosition) {
//         return abs(currentPosition - targetPosition) <= positionTolerance;
//     };

//     // Move the servo to the first target position
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, firstTargetPosition, ST3215_MaxSpeed, ST3215_MaxAcc);

//     // Wait until the servo reaches the first target position within tolerance
//     do {
//         delay(100); // Brief delay to prevent flooding the servo with requests
//         if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
//             Serial.println("Error reading position after moving to position 1.");
//             return ReadBack_Status::ERROR; // Return on failure to read position
//         }
//     } while (!isWithinTolerance(currentPosition, firstTargetPosition));

//     // Move the servo to the second target position
//     m_servo->goPosByCount(ID_UNLOADER_MOTOR, secondTargetPosition, ST3215_MaxSpeed, ST3215_MaxAcc);

//     // Wait until the servo reaches the second target position within tolerance
//     do {
//         delay(100); // Brief delay to prevent flooding the servo with requests
//         if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
//             Serial.println("Error reading position after moving to position 2048.");
//             return ReadBack_Status::ERROR; // Return on failure to read position
//         }
//     } while (!isWithinTolerance(currentPosition, secondTargetPosition));

//     return ReadBack_Status::NORMAL;
// }





ReadBack_Status Unloader::unload() {
  if (m_is_error) return ReadBack_Status::ERROR;
  if (m_servo == nullptr) return ReadBack_Status::NO_SERIAL;
  if (!m_is_init) return ReadBack_Status::NOT_INIT;

  const int positionTolerance = 50;  // Tolerance for position checking
  int16_t currentPosition = 0;       // Variable to hold the current position
  int16_t targetPosition = 0;        // Variable to hold the target position

  // Get the current position
  if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
    Serial.println("Error reading current position.");
    return ReadBack_Status::ERROR;  // Return on failure to read position
  }

  // Determine target position based on current position
  if (currentPosition >= 0 && currentPosition <= 370) {
    targetPosition = 3755;
  } else if (currentPosition >= 3725 && currentPosition <= 3785) {
    targetPosition = 341;
  } else {
    Serial.println("Invalid current position.");
    return ReadBack_Status::ERROR;
  }

  // Move the servo to the target position
  m_servo->goPosByCount(ID_UNLOADER_MOTOR, targetPosition, ST3215_MaxSpeed, ST3215_MaxAcc);

  // Wait until the servo reaches the target position within tolerance
  // do {
  //     delay(100); // Brief delay to prevent flooding the servo with requests
  //     if (m_servo->getPos(ID_UNLOADER_MOTOR, currentPosition) != ReadBack_Status::NORMAL) {
  //         Serial.println("Error reading position after moving to target position.");
  //         return ReadBack_Status::ERROR; // Return on failure to read position
  //     }
  // } while (!(abs(currentPosition - targetPosition) <= positionTolerance));
  delay(1500);
  return ReadBack_Status::NORMAL;
}





void Unloader::resetError() {
  m_is_error = false;
}

bool Unloader::isError() const {
  return m_is_error;
}
