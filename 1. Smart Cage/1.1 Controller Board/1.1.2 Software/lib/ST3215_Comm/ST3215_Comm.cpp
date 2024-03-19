#include "ST3215_Comm.h"

uint8_t ST3215_Comm::calcCRC(uint8_t *msg_buffer, uint8_t len)
{
  uint8_t calSum = 0;
  for (uint8_t ctn = ST3215_MSG_INDEX::ID; ctn <= (len - 2); ++ctn) // From ID to param2
  {

    calSum += msg_buffer[ctn];
  }
  return ~(calSum);
}

void ST3215_Comm::flush(HardwareSerial *serial)
{
  // Clear buffer due to one-wire serial
  while (serial->read() != -1) {}
}

void ST3215_Comm::write(HardwareSerial *serial, uint8_t *msg, uint8_t msg_len)
{
  if (serial == nullptr) return;
  // Normal Case
  this->flush(serial);
  for (uint8_t i = 0; i < msg_len; ++i)
  {
    serial->write(msg[i]);
  }
  delayMicroseconds(5); // the feedback from motor is 25us later
  this->flush(serial);
  delay(5);
}

ReadBack_Status ST3215_Comm::readWord(HardwareSerial *serial, int16_t &recv)
{
  if (serial == nullptr) return ReadBack_Status::NO_SERIAL;
  // Normal Case
  static uint8_t buffer[16];
  static uint8_t ctn = 0;
  while (serial->available())
  {
    buffer[ctn++] = serial->read();
    if (buffer[ST3215_MSG_INDEX::HEADER_H] != 0xFF) { ctn = 0; } // Not correct header
    else if (ctn < MSG_SIZE) {}                                  // Not enough data
    else
    {
#ifdef DEBUG_MSG
      Serial.print("WOW -> ");
      for (auto i : buffer)
      {
        Serial.print(i, HEX);
        Serial.print("-");
      }
      Serial.println();
#endif
      // Got the  correct message
      ctn = 0;
      uint8_t msg[MSG_SIZE];
      memcpy(msg, buffer, sizeof(msg));
      if (calcCRC(msg, sizeof(msg)) == msg[ST3215_MSG_INDEX::CRC])
      {
        recv = (msg[ST3215_MSG_INDEX::PARAM_1]) | (msg[ST3215_MSG_INDEX::PARAM_2] << 8);
        return ReadBack_Status::NORMAL;
      }
      else
        return ReadBack_Status::WRONG_CRC;
    }
  }
  return ReadBack_Status::OUT_OF_INDEX;
}

void ST3215_Comm::writePosMsg(HardwareSerial *serial, uint8_t id, int16_t position, uint16_t speed, uint8_t acc)
{
  uint8_t msg[14]{ 0 };
  msg[ST3215_MSG_INDEX::HEADER_H]    = 0xFF;
  msg[ST3215_MSG_INDEX::HEADER_L]    = 0xFF;
  msg[ST3215_MSG_INDEX::ID]          = id;
  msg[ST3215_MSG_INDEX::LENGTH]      = 0x0A;
  msg[ST3215_MSG_INDEX::INSTRUCTION] = INSTRUCT_WRITE;
  msg[ST3215_MSG_INDEX::PARAM_1]     = 0x29;            // Register ID 0x29
  msg[ST3215_MSG_INDEX::PARAM_2]     = acc;             // uint8_t acc
  msg[7]                             = position & 0xFF; // Little Endian way
  msg[8]                             = position >> 8;
  msg[9]                             = 0;
  msg[10]                            = 0;
  msg[11]                            = speed & 0xFF;
  msg[12]                            = speed >> 8;
  msg[13]                            = ST3215_Comm::calcCRC(msg, sizeof(msg));
  write(serial, msg, sizeof(msg));
}
void ST3215_Comm::writeSpeedMsg(HardwareSerial *serial, uint8_t id, uint16_t speed, uint8_t acc)
{
  uint8_t msg2[8]{ 0 };
  createMsg(id, INSTRUCT_WRITE, 0x29, acc, msg2, sizeof(msg2));
  write(serial, msg2, sizeof(msg2));
  delay(10);
  uint8_t msg[9]{ 0 };
  createWord(id, INSTRUCT_WRITE, 0x2E, (speed & 0xFF), (speed >> 8), msg, sizeof(msg));
  write(serial, msg, sizeof(msg));
}

void ST3215_Comm::createMsg(uint8_t id, uint8_t instruction, uint8_t param1, uint8_t param2, uint8_t *msg, uint8_t msg_len)
{
  // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [PARAM] [PARAM] [CRC]
  msg[ST3215_MSG_INDEX::HEADER_H]    = 0xFF;
  msg[ST3215_MSG_INDEX::HEADER_L]    = 0xFF;
  msg[ST3215_MSG_INDEX::ID]          = id;
  msg[ST3215_MSG_INDEX::LENGTH]      = 0x04;
  msg[ST3215_MSG_INDEX::INSTRUCTION] = instruction;
  msg[ST3215_MSG_INDEX::PARAM_1]     = param1;
  msg[ST3215_MSG_INDEX::PARAM_2]     = param2; // 2bytes
  msg[ST3215_MSG_INDEX::CRC]         = ST3215_Comm::calcCRC(msg, msg_len);
}

void ST3215_Comm::createWord(uint8_t id, uint8_t instruction, uint8_t param1, uint8_t param2, uint8_t param3, uint8_t *msg, uint8_t msg_len)
{
  // [0xFF] [0xFF] [ID] [LEN] [INSTRUCTION] [PARAM] [PARAM] [CRC]
  msg[ST3215_MSG_INDEX::HEADER_H]    = 0xFF;
  msg[ST3215_MSG_INDEX::HEADER_L]    = 0xFF;
  msg[ST3215_MSG_INDEX::ID]          = id;
  msg[ST3215_MSG_INDEX::LENGTH]      = 0x05;
  msg[ST3215_MSG_INDEX::INSTRUCTION] = instruction;
  msg[ST3215_MSG_INDEX::PARAM_1]     = param1;
  msg[ST3215_MSG_INDEX::PARAM_2]     = param2; // 2bytes
  msg[ST3215_MSG_INDEX::PARAM_2 + 1] = param3; // 2bytes
  msg[ST3215_MSG_INDEX::CRC + 1]     = ST3215_Comm::calcCRC(msg, msg_len);
}