#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include "CommDefine.h"
#include "Define.h"
#include <Arduino.h>
//#include "Servo.h"

class StarWheelServo;
class Unloader;
class AnalogSensors;
class Valve;

enum class ActionType { NO_MSG = -2, NO_SERIAL = -1, VOID = 0, ACTION, SENSE };

class Communication {

public:
  static const uint8_t MSG_SIZE{8};

  /* ---------------------------------------------------------------------------------------------- */
  void init(Stream *ar_serial);
  void setStarWheelServo(StarWheelServo *ar_starwheel);
  void setUnloader(Unloader *ar_unloader);
  void setSensors(AnalogSensors *ar_sensor);
  void setValve(Valve *ar_valve);
  void writeByteArray(uint8_t *pMsg, uint8_t msg_size);
  //  void setServo(Servo *servo);

  // Always call
  void update();

  // Messages
  void replyACK();
  void replyReadbackStatus(ReadBack_Status status);

private:
  Stream *m_serial{nullptr};
  StarWheelServo *m_starwheel{nullptr};
  Unloader *m_unloader{nullptr};
  AnalogSensors *m_sensor{nullptr};
  Valve *m_valve{nullptr}; // Add Valve reference
                           //  Servo          *m_servo{ nullptr };

  // Comm
  uint8_t m_msg[MSG_SIZE]{0};
  uint8_t m_counter{0};
  stMsgRecv m_stMsg;
  const char m_ack[MSG_SIZE] = "ACK";
  /* -------------------------------------------------------------------------------------------- */
  uint16_t calculateCRC16(uint8_t *data, uint8_t dataSize);
  bool isCRCCorrect();

  void pri_ReadDataIntoBuffer();
  bool pri_isHeaderCorrect() const;
  bool pri_isMsgValid();
  void pri_actionMsgHandler();

  void pri_valveActionHandler();
  void pri_valveTurnOnHandler();
  void pri_valveTurnOffHandler();
  void pri_valvePulseHandler();

  void pri_starWheelActionHandler();
  void pri_starWheelStepHandler();
  void pri_starWheelHomingHandler();
  void pri_starWheelInitHandler();
  void pri_starWheelTimingStepHandler();
  void pri_starWheelResetErrorHandler();
  void pri_starWheelMoveCount();
  void pri_starWheelMoveCountRelative();
  void pri_starWheelSaveOffsetCount();

  void pri_unloaderActionHandler();
  void pri_unloaderUnloadHandler();
  void pri_unloaderHomeHandler();
  void pri_unloaderResetErrorHandler();
  void pri_getUnloaderPosHandler();

  void pri_senseMsgHandler();

  void pri_starWheelSensorHandler();
  void pri_starWheelErrorHandler();

  void pri_unloaderSensorHandler();
  void pri_unloaderErrorHandler();

  void pri_GPIOSensorHandler();
  /* -------------------------------------------------------------------------------------------- */

  void starWheelTurnHandler();
};

#endif
