#ifndef SERVO_H
#define SERVO_H

#include "Define.h"
#include "ST3215_Comm.h"

#define ST3215_MaxSpeed 3400
#define ST3215_MaxAcc   150

class Servo : private ST3215_Comm
{
public:
  // Basic
  virtual void setSerial(HardwareSerial *serial);
  virtual void changeID(uint8_t from_id, uint8_t to_id);

  // Mode
  virtual ReadBack_Status setServoMode(const uint8_t &id, bool remove_limit);
  virtual ReadBack_Status setWheelMode(const uint8_t &id);
  virtual ReadBack_Status setZero(const uint8_t &id);

  // Action
  virtual ReadBack_Status moveSpeed(const uint8_t &id, int16_t count, uint8_t acc);
  virtual ReadBack_Status goPosByCount(const uint8_t &id, int16_t count, uint16_t speed, uint8_t acc);
  virtual ReadBack_Status stop(const uint8_t &id);
  virtual ReadBack_Status release(const uint8_t &id);
  virtual void            overloadProcedure(const uint8_t &id);
  virtual ReadBack_Status delayWithLoadDetection(const uint8_t &id, uint16_t ms, uint16_t load_limit = NULL);

  // Info
  ReadBack_Status getPos(const uint8_t &id, int16_t &position);
  ReadBack_Status getLoad(const uint8_t &id, int16_t &load);
  uint16_t        calcDelayTime(const int16_t &count, const uint16_t &speed, const uint8_t &acc);
  uint16_t        calcVelocity(const uint16_t &time, const uint8_t &acc);
  uint16_t        calcDynamicLoad(const uint16_t &time_ms);

private:
  HardwareSerial *m_serial{ nullptr };
};
#endif
