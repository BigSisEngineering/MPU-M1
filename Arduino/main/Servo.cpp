#include "Servo.h"

void Servo::setSerial(HardwareSerial *serial)
{
  if (m_serial == nullptr) this->m_serial = serial;
}

void Servo::changeID(uint8_t from_id, uint8_t to_id)
{
  // SMS_STS::unLockEprom(from_id);                  // unlock EPROM-SAFE
  // SMS_STS::writeByte(from_id, SMS_STS_ID, to_id); // ID
  // SMS_STS::LockEprom(to_id);                      // EPROM-SAFE locked
}

ReadBack_Status Servo::setServoMode(const uint8_t &id, bool remove_limit)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  // Message send
  // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [REGISTER] [PARAM] [CRC]
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_MODE, MODE::SERVO, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  /* -------------------------------------------------------------------------------------------- */
  uint8_t msg2[9]{ 0 };
  if (remove_limit)
  {
    ST3215_Comm::createWord(id, ST3215_Comm::INSTRUCT_WRITE, ST3215_Comm::REG_LIMIT, 0, 0, msg2, sizeof(msg2));
    ST3215_Comm::write(m_serial, msg2, sizeof(msg2));
  }
  /* -------------------------------------------------------------------------------------------- */
  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::setWheelMode(const uint8_t &id)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_MODE, MODE::WHEEL, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::setZero(const uint8_t &id)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_TORQUE, 128, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::moveSpeed(const uint8_t &id, int16_t count, uint8_t acc)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  count = constrain(count, -ST3215_MaxSpeed, ST3215_MaxSpeed);
  if (count < 0)
  {
    count = -count;
    count |= (1 << 15);
  }
  ST3215_Comm::writeSpeedMsg(m_serial, id, count, acc);

  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::goPosByCount(const uint8_t &id, int16_t count, uint16_t speed, uint8_t acc)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check

  if (count < 0)
  {
    count = -count;
    count |= (1 << 15);
  }
  speed = constrain(speed, 0, ST3215_MaxSpeed);
  acc   = constrain(acc, 0, ST3215_MaxAcc);
  ST3215_Comm::writePosMsg(m_serial, id, count, speed, acc);
  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::stop(const uint8_t &id)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  // ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_TORQUE, 0, msg, sizeof(msg));
  // ST3215_Comm::write(m_serial, msg, sizeof(msg));
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_TORQUE, 1, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  return ReadBack_Status::NORMAL;
}

ReadBack_Status Servo::release(const uint8_t &id)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  // ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_TORQUE, 1, msg, sizeof(msg));
  // ST3215_Comm::write(m_serial, msg, sizeof(msg));
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_WRITE, REG_TORQUE, 0, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  return ReadBack_Status::NORMAL;
}

void Servo::overloadProcedure(const uint8_t &id)
{
  this->stop(id);
  this->release(id);
}

ReadBack_Status Servo::delayWithLoadDetection(const uint8_t &id, uint16_t ms, uint16_t load_limit = NULL)
{
  if (load_limit == NULL)
  {
    load_limit = this->calcDynamicLoad(ms);
  }
  uint32_t timestamp = millis();
  int16_t  load{ 0 };
  while ((millis() - timestamp) < ms)
  {
    this->getLoad(id, load);
    if (load > load_limit)
    {
      this->overloadProcedure(id);
      return ReadBack_Status::OVERLOAD;
    }
  }
  return ReadBack_Status::NORMAL;
}

//ReadBack_Status Servo::getPos(const uint8_t &id, int16_t &position)
//{
//  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
//  // Message send
//  // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [REGISTER] [LEN] [CRC]
//  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
//  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_READ, ST3215_Comm::REG_POSITION, 2, msg, sizeof(msg));
//  ST3215_Comm::write(m_serial, msg, sizeof(msg));
//  ReadBack_Status res = ST3215_Comm::readWord(m_serial, position);
//  if (position & (1 << 15)) position = -(position & ~(1 << 15));
//  return (res);
//}


ReadBack_Status Servo::getPos(const uint8_t &id, int16_t &position) {
    if (m_serial == nullptr) {
        Serial.println("Serial port not initialized.");
        return ReadBack_Status::NO_SERIAL; // Sanity Check
    }

    // Message send
    // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [REGISTER] [LEN] [CRC]
    uint8_t msg[ST3215_Comm::MSG_SIZE] = {0};
    ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_READ, ST3215_Comm::REG_POSITION, 2, msg, sizeof(msg));

    Serial.print("Sending position request: ");
    for (int i = 0; i < sizeof(msg); i++) {
        Serial.print(msg[i], HEX);
        Serial.print(" ");
    }
    Serial.println();

    ST3215_Comm::write(m_serial, msg, sizeof(msg));

    // Read position from the serial
    ReadBack_Status res = ST3215_Comm::readWord(m_serial, position);
    if (res == ReadBack_Status::NORMAL) {
        if (position & (1 << 15)) { // Check if the highest bit is set (negative number in two's complement)
            position = -(position & ~(1 << 15)); // Convert to a negative integer
        }
        Serial.print("Position read successfully: ");
        Serial.println(position);
    } else {
        Serial.println("Failed to read position.");
    }

    return res;
}




ReadBack_Status Servo::getLoad(const uint8_t &id, int16_t &load)
{
  if (m_serial == nullptr) return ReadBack_Status::NO_SERIAL; // Sanity Check
  // Message send
  // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [REGISTER] [LEN] [CRC]
  uint8_t msg[ST3215_Comm::MSG_SIZE] = { 0 };
  ST3215_Comm::createMsg(id, ST3215_Comm::INSTRUCT_READ, ST3215_Comm::REG_LOAD, 2, msg, sizeof(msg));
  ST3215_Comm::write(m_serial, msg, sizeof(msg));
  ReadBack_Status res = ST3215_Comm::readWord(m_serial, load);
  load &= 0x03FF; // flip the first 5 bits to zero
  if (load & (1 << 10)) load = -(load & ~(1 << 10));
  return (res);
}

uint16_t Servo::calcDelayTime(const int16_t &count, const uint16_t &speed, const uint8_t &acc)
{
  //(count*1000/velocity) + (velocity*15/acc)
  return ((abs(count) * abs((float)1000.0 / speed)) + abs(speed * 15 / acc));
}

uint16_t Servo::calcVelocity(const uint16_t &time, const uint8_t &acc)
{
  // the quadratic formula is
  // 1.5e^-4 (x^2) - y(x) + 512 = 0
  // constrain the time is 600 <= t <= 5000 to ensure the depth is correct
  // we are in the lower region of x, that's why we take the minimum one.
  // x = (-b - sqrt( b^2 - 4*a*c)) / (2*a)
  float           b    = -1 * (float)(time) / 1000;
  constexpr float ac   = 4 * (1.5e-4) * 512;
  float           disc = (b * b) - ac;
  return ((-b - sqrt(disc)) / (2 * (1.5e-4)));
}

uint16_t Servo::calcDynamicLoad(const uint16_t &time_ms)
{
  // the inversely proportional fit formula is
  // y= (207458.549078 / x) - 3.393769
  // y is load, x is time in ms
  // make a offset for load is multiply by 1.15 and 400 increamet

  float a = (float)(207458.549078) / time_ms;
  float b = a - 3.393769;

  return (uint16_t)(b * 1.5) + 400;
}
