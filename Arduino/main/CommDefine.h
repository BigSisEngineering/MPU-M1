#ifndef COMM_DEFINE_H
#define COMM_DEFINE_H
#include <Arduino.h>

#define PARAM_QTY 3

// Header
#define HEADER_ACTION            0xAA
#define HEADER_SENSE             0xBB
#define HEADER_RESPONS           0xCC
// Target
#define TARGET_STARWHEEL         0x01
#define TARGET_UNLOADER          0x02
#define TARGET_GPIO              0x03
// Action
#define ACTION_MOVE              0x01
#define ACTION_TURN              0x02
#define ACTION_HOME              0x03
#define ACTION_COUNT             0x04
#define ACTION_TIME              0x05
#define ACTION_RESET_ERROR       0x06
#define ACTION_MOVE_COUNT        0x07
#define ACTION_SAVE_OFFSET_COUNT 0x08
// Sense
#define SENSE_ERROR_STATUS       0x01

typedef struct MsgRecv
{
  MsgRecv(){};
  uint8_t  header{ 0 };
  uint8_t  target{ 0 };
  uint8_t  action{ 0 };
  uint8_t  params[PARAM_QTY]{ 0 };
  uint16_t crc{ 0 };
} stMsgRecv;

typedef struct MsgSend
{
  MsgSend(){};
  uint8_t header{ HEADER_RESPONS };
  uint8_t target{ 0 };
  uint8_t action{ 0 };
  uint8_t infos[PARAM_QTY]{ 0 };
} stMsgSend;

#endif