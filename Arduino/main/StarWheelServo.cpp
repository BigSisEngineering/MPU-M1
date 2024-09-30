#include "DebounceInput.h"
#include "Servo.h"
#include "StarWheelServo.h"
#include "Valve.h"
#include <EEPROM.h>

void StarWheelServo::init(uint8_t sensor_pin)
{
  m_sensor_pin = sensor_pin;
  pinMode(m_sensor_pin, INPUT);
  m_speed = ST3215_MaxSpeed;
  m_acc   = ST3215_MaxAcc;
  EEPROM.get(0, SENSOR_SLOT_OFFSET);
}

void StarWheelServo::setServo(Servo *ar_servo)
{
  m_servo = ar_servo;
}

void StarWheelServo::setValve(Valve *ar_valve)
{
  m_valve = ar_valve;
}

void StarWheelServo::setCW()
{
  m_direction = -1;
}

void StarWheelServo::setCCW()
{
  m_direction = 1;
}

// ReadBack_Status StarWheelServo::homing(bool use_constant_blast = true)
// {
//   if ((m_servo == nullptr) || (m_valve == nullptr) || (m_is_error)) return ReadBack_Status::ERROR; // No servo object
//   // Sensor detected
//   if (debounceDigitalRead(m_sensor_pin, true))
//   {
//     resetCounter();
//     setCCW();
//     m_move_counter += (m_direction * 2 * 512);
//     if (m_valve != nullptr) m_valve->blast();
//     m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, m_move_counter, m_speed, m_acc);
//     m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR,
//                                     m_servo->calcDelayTime(m_move_counter, m_speed, m_acc),
//                                     m_servo->calcDynamicLoad(600));
//   }

//   // Somewhere in the middle
//   m_servo->setWheelMode(ID_STAR_WHEEL_MOTOR); // Speed Mode
//   setCW();
//   if ((m_valve != nullptr) && (use_constant_blast))
//     m_valve->turnOn();
//   m_servo->moveSpeed(ID_STAR_WHEEL_MOTOR, (m_direction) * 800, 15); // Go backward
//   uint32_t        timer = millis();
//   ReadBack_Status status{ ReadBack_Status::IDLE };
//   while (status == ReadBack_Status::IDLE)
//   {
//     bool ans = debounceDigitalRead(m_sensor_pin, true);
//     // Cannot be trigger
//     if ((millis() - timer) > (60 * 1000)) { status = ReadBack_Status::TIMEOUT; }
//     // Triggered by the sensor
//     if (ans) { status = ReadBack_Status::NORMAL; }
//     // overload
//     if (m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR,
//                                         1,
//                                         m_servo->calcDynamicLoad(600)) == ReadBack_Status::OVERLOAD)
//     {
//       m_is_error = true;
//       if (m_valve != nullptr) m_valve->turnOff();
//       return ReadBack_Status::OVERLOAD;
//     }
//   }

//   // already retracted && set the count
//   m_servo->moveSpeed(ID_STAR_WHEEL_MOTOR, 0, 15);
//   m_servo->setServoMode(ID_STAR_WHEEL_MOTOR, true);
//   resetCounter();
//   delay(30);
//   // FIXME having offset between the screw and the slot
//   m_move_counter -= this->SENSOR_SLOT_OFFSET;
//   m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, m_move_counter, m_speed, m_acc);
//   uint16_t delay_time = m_servo->calcDelayTime(this->SENSOR_SLOT_OFFSET, m_speed, m_acc);
//   m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, delay_time);
//   if (m_valve != nullptr) m_valve->turnOff();
//   resetCounter();
//   m_is_init      = true;
//   m_step_counter = 0;
//   return status;
// }

ReadBack_Status StarWheelServo::homing(bool use_constant_blast = true)
{
    // Check initial conditions for errors
    if ((m_servo == nullptr) || (m_valve == nullptr) || (m_is_error)) {
        return ReadBack_Status::ERROR; // No servo object or other error conditions
    }
    // Read the initial state of the sensor
    bool initialSensorState = debounceDigitalRead(m_sensor_pin, true);
    setCW(); 
    // Start valve operation if constant blast is used
    if (use_constant_blast && m_valve != nullptr) {
        m_valve->turnOn();
    }
    // Begin moving the servo in the set direction
    m_servo->setWheelMode(ID_STAR_WHEEL_MOTOR); // Set servo to wheel mode for continuous rotation
    uint32_t timer = millis();
    ReadBack_Status status = ReadBack_Status::IDLE;
    while (status == ReadBack_Status::IDLE) {
        bool currentSensorState = debounceDigitalRead(m_sensor_pin, true);
        // Continue moving while checking the sensor
        m_servo->moveSpeed(ID_STAR_WHEEL_MOTOR, m_direction * 800, 15);
        // Check if the sensor state has changed from its initial state
        if (currentSensorState != initialSensorState) {
            status = ReadBack_Status::NORMAL; // State change detected, homing successful
            break;
        }
        // Check for timeout (60 seconds)
        if ((millis() - timer) > 60000) {
            status = ReadBack_Status::TIMEOUT;
            break;
        }
        // Check for overload condition
        if (m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, 1, m_servo->calcDynamicLoad(600)) == ReadBack_Status::OVERLOAD) {
            m_is_error = true;
            if (m_valve != nullptr) {
                m_valve->turnOff();
            }
            return ReadBack_Status::OVERLOAD;
        }
    }
    // Stop and reset servo position after movement
    m_servo->moveSpeed(ID_STAR_WHEEL_MOTOR, 0, 15);
    m_servo->setServoMode(ID_STAR_WHEEL_MOTOR, true);
    resetCounter();
    delay(30); // Short delay to allow mechanical settling
    // Adjust for any mechanical offsets
    m_move_counter -= this->SENSOR_SLOT_OFFSET;
    m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, m_move_counter, m_speed, m_acc);
    uint16_t delay_time = m_servo->calcDelayTime(this->SENSOR_SLOT_OFFSET, m_speed, m_acc);
    m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, delay_time);
    // Cleanup valve operation if used
    if (m_valve != nullptr) {
        m_valve->turnOff();
    }
    resetCounter();
    m_is_init = true;
    m_step_counter = 0;
    return status;
}


ReadBack_Status StarWheelServo::moveSteps(int8_t step = 1)
{
  if (!m_is_init) return ReadBack_Status::NOT_INIT;         // Not init
  if (m_is_error) return ReadBack_Status::ERROR;            // Having error
  if (m_servo == nullptr) return ReadBack_Status::NOT_INIT; // No object

  if (isNextMoveCauseOverflow(step)) resetCounter();
  if ((m_step_counter + step) >= MAX_STEPS)
  {
    return this->homing(false);
  }
  m_move_counter += (m_direction) * (step * COUNT_FOR_ONE_SLOT);
  m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, m_move_counter, m_speed, m_acc);
  uint16_t        delay_time = m_servo->calcDelayTime((m_direction) * (step * COUNT_FOR_ONE_SLOT), m_speed, m_acc);
  ReadBack_Status status     = m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, delay_time);
  if (status == ReadBack_Status::OVERLOAD)
  {
    {
      m_is_error = true;
      return ReadBack_Status::OVERLOAD;
    }
  }
  m_servo->release(ID_STAR_WHEEL_MOTOR);
  m_step_counter += step;
  return (ReadBack_Status::NORMAL);
}

ReadBack_Status StarWheelServo::moveStep(uint16_t time_ms)
{
  if (!m_is_init) return ReadBack_Status::NOT_INIT;      // Not init
  if (m_is_error) return ReadBack_Status::ERROR;         // Having error
  if (m_servo == nullptr) return ReadBack_Status::ERROR; // No object
  if (isNextMoveCauseOverflow(1)) resetCounter();
  if ((m_step_counter + 1) >= MAX_STEPS)
  {
    if (m_valve != nullptr) m_valve->blast();
    return this->homing(false);
  }
  m_move_counter += (m_direction) * (1 * COUNT_FOR_ONE_SLOT);
  time_ms        = constrain(time_ms, 600, 5000); // Boundary condition for the time
  uint16_t speed = m_servo->calcVelocity(time_ms, m_acc);
  if (m_valve != nullptr) m_valve->blast();
  m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, m_move_counter, speed, m_acc);
  uint16_t        delay_time = m_servo->calcDelayTime((m_direction) * (COUNT_FOR_ONE_SLOT), speed, m_acc);
  ReadBack_Status status     = m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, delay_time, 600); // FIXME - 600 is a magic number
  // m_servo->release(ID_STAR_WHEEL_MOTOR);
  m_step_counter += 1;
  return (status);
}

ReadBack_Status StarWheelServo::moveCount(uint16_t count)
{
  if (!m_is_init) return ReadBack_Status::NOT_INIT;      // Not init
  if (m_is_error) return ReadBack_Status::ERROR;         // Having error
  if (m_servo == nullptr) return ReadBack_Status::ERROR; // No object
  int16_t pos = m_move_counter + (m_direction * count);
  m_servo->goPosByCount(ID_STAR_WHEEL_MOTOR, pos, m_speed, m_acc);
  uint16_t delay_time = m_servo->calcDelayTime((m_direction * count), m_speed, m_acc);
  m_servo->delayWithLoadDetection(ID_STAR_WHEEL_MOTOR, delay_time, 600); // FIXME - 600 is a magic number
}

ReadBack_Status StarWheelServo::m_init()
{
  if ((m_servo == nullptr) || (m_valve == nullptr) || (m_is_error)) {
        return ReadBack_Status::ERROR; // No servo object or other error conditions
    }
  m_is_init = true;
  return ReadBack_Status::NORMAL;
}

void StarWheelServo::spin(int8_t speed)
{
}

bool StarWheelServo::isNextMoveCauseOverflow(int8_t step)
{
  long result = (long)m_move_counter + (long)((m_direction) * (long)(step * COUNT_FOR_ONE_SLOT));
  return (result >= 30000 || result <= -30000); // Exceed the int16 range
}

bool StarWheelServo::isInited() const { return m_is_init; }
bool StarWheelServo::isError() const { return m_is_error; }

void StarWheelServo::resetCounter()
{
  delay(100);
  if (m_servo == nullptr) return;
  // Set current position to be the centre of slot
  // Reset the counter to 2048
  m_servo->setZero(ID_STAR_WHEEL_MOTOR);
  m_move_counter = 2047;
}

void StarWheelServo::resetError() { m_is_error = false; }
