#ifndef ST3215_COMM_H
#define ST3215_COMM_H

#include "Define.h"
#include <Arduino.h>

class ST3215_Comm
{
public:
  enum ST3215_MSG_INDEX
  {
    HEADER_H = 0,
    HEADER_L,
    ID,
    LENGTH,
    INSTRUCTION,
    PARAM_1,
    PARAM_2,
    CRC
  };

  // Mode List
  enum MODE
  {
    SERVO = 0,
    WHEEL
  };

  const uint8_t MSG_SIZE       = 8;
  // Instruction List
  const uint8_t INSTRUCT_PING  = 0x01;
  const uint8_t INSTRUCT_READ  = 0x02;
  const uint8_t INSTRUCT_WRITE = 0x03;

  // Register List
  const uint8_t REG_LIMIT    = 0x0B; // 1bytes
  const uint8_t REG_MODE     = 0x21; // 1bytes
  const uint8_t REG_TORQUE   = 0x28; // 1bytes
  const uint8_t REG_POSITION = 0x38; // 2bytes
  const uint8_t REG_SPEED    = 0x3A; // 2bytes
  const uint8_t REG_LOAD     = 0x3C; // 2bytes
  const uint8_t REG_VOLTAGE  = 0x3E; // 1bytes
  const uint8_t REG_TEMP     = 0x3F; // 1bytes

  virtual uint8_t         calcCRC(uint8_t *msg_buffer, uint8_t len);
  virtual void            flush(HardwareSerial *serial);
  virtual void            write(HardwareSerial *serial, uint8_t *msg, uint8_t msg_len);
  virtual ReadBack_Status readWord(HardwareSerial *serial, int16_t &recv);

  virtual void writePosMsg(HardwareSerial *serial, uint8_t id, int16_t position, uint16_t speed, uint8_t acc);
  virtual void writeSpeedMsg(HardwareSerial *serial, uint8_t id, uint16_t speed, uint8_t acc);

  virtual void createMsg(uint8_t id, uint8_t instruction, uint8_t param1, uint8_t param2, uint8_t *msg, uint8_t msg_len);
  virtual void createWord(uint8_t id, uint8_t instruction, uint8_t param1, uint8_t param2, uint8_t param3, uint8_t *msg, uint8_t msg_len);
};
#endif