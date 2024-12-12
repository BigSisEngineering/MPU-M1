#include <EEPROM.h>
#include <avr/wdt.h> // watchdog timer library
/* ---------------------------------------------------------------------------------------------- */
#include "AnalogSensors.h"
#include "Communication.h"
#include "StarWheelServo.h"
#include "UnloaderServo.h"
#include "Valve.h"

void Communication::init(Stream *serial) { m_serial = serial; }
void Communication::setStarWheelServo(StarWheelServo *starwheel) { m_starwheel = starwheel; }
void Communication::setUnloader(Unloader *unloader) { m_unloader = unloader; }
void Communication::setSensors(AnalogSensors *ar_sensor) { m_sensor = ar_sensor; }
void Communication::setValve(Valve *ar_valve) { m_valve = ar_valve; }

void Communication::update() {
  // Capture data into buffer
  pri_ReadDataIntoBuffer();
  // Check any message
  if (!pri_isMsgValid())
    return;
  /* ############################################################################################ */
  /*                                         MAIN HANDLER                                         */
  /* ############################################################################################ */
  switch (m_stMsg.header) {
  case HEADER_ACTION:
    pri_actionMsgHandler();
    break;
  case HEADER_SENSE:
    pri_senseMsgHandler();
    break;
  }

  // TODO 3) Overload Handler?
}

void Communication::replyACK() {
  if (m_serial == nullptr)
    return;
  m_serial->write(m_ack, MSG_SIZE);
}

void Communication::replyReadbackStatus(ReadBack_Status status) {
  uint8_t msg[MSG_SIZE]{0};
  msg[0] = HEADER_RESPONS;
  msg[1] = 0;
  // msg[2]       = 0;
  msg[3] = getReadback(status);
  // msg[4]       = 0;
  // msg[5]       = 0;
  uint16_t crc = calculateCRC16(msg, 6);
  msg[6] = crc;
  msg[7] = crc >> 8;
  writeByteArray(msg, sizeof(msg));
}

void Communication::writeByteArray(uint8_t *pMsg, uint8_t msg_size) {
  if (m_serial == nullptr)
    return;
  m_serial->flush();
  m_serial->write(pMsg, msg_size);
}

uint16_t Communication::calculateCRC16(uint8_t *data, uint8_t dataSize) {
  uint16_t crc{0xFFFF};
  for (uint8_t index = 0; index < dataSize; ++index) {
    crc ^= data[index];
    for (uint8_t i = 0; i < 8; ++i) // check bit
    {
      if (crc & 0x0001) {
        crc >>= 1;
        crc ^= 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }
  return (crc & 0xFFFF);
}

bool Communication::isCRCCorrect() {
  uint16_t crc = calculateCRC16(m_msg, MSG_SIZE - 2);

  return (crc == m_stMsg.crc);
}
/* ---------------------------------------------------------------------------------------------- */

void Communication::pri_ReadDataIntoBuffer() {
  if (m_serial == nullptr)
    return; // Sanity check
  if (m_serial->available() == 0)
    return; // No data
  m_msg[m_counter++] = m_serial->read();
  if ((m_counter > 0) && !pri_isHeaderCorrect())
    m_counter = 0;
}

bool Communication::pri_isHeaderCorrect() const { return ((m_msg[0] == HEADER_ACTION) || (m_msg[0] == HEADER_SENSE)); }

bool Communication::pri_isMsgValid() {
  if (m_counter < MSG_SIZE)
    return false;
  m_counter = 0;
  memcpy(&m_stMsg, m_msg, sizeof(m_msg));
  return (isCRCCorrect()); // Valid or not depends on thr CRC
}

void Communication::pri_actionMsgHandler() {
  switch (m_stMsg.target) {
  case TARGET_STARWHEEL:
    pri_starWheelActionHandler();
    break;
  case TARGET_UNLOADER:
    pri_unloaderActionHandler();
    break;
  case TARGET_VALVE:
    pri_valveActionHandler();
    break;
  default:
    break;
  }
}

void Communication::pri_starWheelActionHandler() {
  if (m_starwheel == nullptr)
    return;

  switch (m_stMsg.action) {
  case ACTION_MOVE:
    pri_starWheelStepHandler();
    break;
  case ACTION_TURN:
    break; // TODO
  case ACTION_HOME:
    pri_starWheelHomingHandler();
    break;
  case ACTION_TIME:
    pri_starWheelTimingStepHandler();
    break;
  case ACTION_INIT:
    pri_starWheelInitHandler();
    break;
  case ACTION_RESET_ERROR:
    pri_starWheelResetErrorHandler();
    break;
  case ACTION_MOVE_COUNT:
    pri_starWheelMoveCount();
    break;
  case ACTION_MOVE_COUNT_REL:
    pri_starWheelMoveCountRelative();
    break;
  case ACTION_SAVE_OFFSET_COUNT:
    pri_starWheelSaveOffsetCount();
    break;
    //  case ACTION_READ_POS: pri_getPosHandler(); break;
  default:
    break;
  }
}

void Communication::pri_starWheelStepHandler() {
  // uint8_t steps = constrain(m_stMsg.params[0], 0, m_starwheel->MAX_STEPS);
  int8_t steps = m_stMsg.params[0];
  m_starwheel->moveSteps(steps);
  replyACK();
}

void Communication::pri_starWheelHomingHandler() {
  ReadBack_Status status = m_starwheel->homing();
  replyReadbackStatus(status);
}

void Communication::pri_starWheelInitHandler() {
  ReadBack_Status status = m_starwheel->m_init();
  replyReadbackStatus(status);
}

void Communication::pri_starWheelTimingStepHandler() {
  uint16_t time = m_stMsg.params[1] << 8 | m_stMsg.params[0];
  ReadBack_Status status = m_starwheel->moveStep(time);
  replyReadbackStatus(status);
}

void Communication::pri_starWheelResetErrorHandler() {
  m_starwheel->resetError();
  replyACK();
}

void Communication::pri_starWheelMoveCount() {
  uint16_t count = m_stMsg.params[1] << 8 | m_stMsg.params[0];
  m_starwheel->moveCount(count);
  replyACK();
}

void Communication::pri_starWheelMoveCountRelative() {
  uint16_t count = m_stMsg.params[1] << 8 | m_stMsg.params[0];
  m_starwheel->moveCountRelative(count);
  replyACK();
}

void Communication::pri_starWheelSaveOffsetCount() {
  uint16_t count = m_stMsg.params[1] << 8 | m_stMsg.params[0];
  EEPROM.put(0, count);
  replyACK();
  delay(100);
  // Enable the watchdog timer to reset the Arduino
  wdt_enable(WDTO_15MS); // Set the watchdog timer to 15 milliseconds
  while (1) {
  } // Wait for the watchdog to reset the Arduino
}

void Communication::pri_unloaderActionHandler() {
  if (m_unloader == nullptr)
    return;
  switch (m_stMsg.action) {
  case ACTION_MOVE:
    pri_unloaderUnloadHandler();
    break;
  case ACTION_HOME:
    pri_unloaderHomeHandler();
    break;
  case ACTION_RESET_ERROR:
    pri_unloaderResetErrorHandler();
    break;
  case ACTION_READ_POS:
    pri_getUnloaderPosHandler();
    break;
  default:
    break;
  }
}

void Communication::pri_unloaderUnloadHandler() {
  ReadBack_Status status = m_unloader->unload();
  replyReadbackStatus(status);
}

void Communication::pri_unloaderHomeHandler() {
  //   case 0x00: m_unloader->homingBySensor(); break; // NOTE - Currently disable
  ReadBack_Status status = m_unloader->homing();
  replyReadbackStatus(status);
}

void Communication::pri_unloaderResetErrorHandler() {
  m_unloader->resetError();
  replyACK();
}

void Communication::pri_getUnloaderPosHandler() {
  if (m_unloader == nullptr)
    return;
  int16_t position = m_unloader->getUnloaderPos();
  uint8_t msg[MSG_SIZE] = {HEADER_RESPONS, TARGET_UNLOADER, (uint8_t)(position & 0xFF), (uint8_t)(position >> 8)};
  uint16_t crc = calculateCRC16(msg, 5);
  msg[5] = crc & 0xFF;
  msg[6] = (crc >> 8) & 0xFF;
  // Send position back via serial
  writeByteArray(msg, sizeof(msg));
}

void Communication::pri_senseMsgHandler() {
  switch (m_stMsg.target) {
  case TARGET_STARWHEEL:
    pri_starWheelSensorHandler();
    break;
  case TARGET_UNLOADER:
    pri_unloaderSensorHandler();
    break;
  case TARGET_GPIO:
    pri_GPIOSensorHandler();
    break;
  case TARGET_VALVE:
    pri_valveActionHandler();
    break;
  default:
    break;
  }
}

void Communication::pri_starWheelSensorHandler() {
  switch (m_stMsg.action) {
  case SENSE_ERROR_STATUS:
    pri_starWheelErrorHandler();
    break;
  }

  // if (m_starwheel == nullptr) return;
  // uint8_t msg[MSG_SIZE]{ 0 };
  // msg[0]       = HEADER_RESPONS;
  // msg[1]       = TARGET_STARWHEEL;
  // // msg[2] = 0; // TODO - More info later
  // msg[3]       = m_starwheel->getStepCount();
  // uint16_t crc = calculateCRC16(msg, 6);
  // msg[6]       = crc;
  // msg[7]       = crc >> 8;
  // writeByteArray(msg, sizeof(msg));
}

void Communication::pri_starWheelErrorHandler() {
  if (m_starwheel == nullptr)
    return;
  uint8_t msg[MSG_SIZE]{0};
  msg[0] = HEADER_RESPONS;
  msg[1] = TARGET_GPIO;
  msg[2] = m_starwheel->isError();
  // msg[3]       = 0;
  // msg[4]       = 0;
  // msg[5]       = 0;
  uint16_t crc = calculateCRC16(msg, 6);
  msg[6] = crc;
  msg[7] = crc >> 8;
  writeByteArray(msg, sizeof(msg));
}

void Communication::pri_unloaderSensorHandler() {
  switch (m_stMsg.action) {
  case SENSE_ERROR_STATUS:
    pri_unloaderErrorHandler();
    break;
  }
}
void Communication::pri_unloaderErrorHandler() {
  if (m_unloader == nullptr)
    return;
  uint8_t msg[MSG_SIZE]{0};
  msg[0] = HEADER_RESPONS;
  msg[1] = TARGET_GPIO;
  msg[2] = m_unloader->isError();
  // msg[3]       = 0;
  // msg[4]       = 0;
  // msg[5]       = 0;
  uint16_t crc = calculateCRC16(msg, 6);
  msg[6] = crc;
  msg[7] = crc >> 8;
  writeByteArray(msg, sizeof(msg));
}

void Communication::pri_GPIOSensorHandler() {
  if (m_sensor == nullptr)
    return;
  uint8_t msg[MSG_SIZE]{0};
  msg[0] = HEADER_RESPONS;
  msg[1] = TARGET_GPIO;
  msg[2] = m_sensor->getValue(3);
  msg[3] = m_sensor->getValue(2);
  msg[4] = m_sensor->getValue(1);
  msg[5] = m_sensor->getValue(0);
  uint16_t crc = calculateCRC16(msg, 6);
  msg[6] = crc;
  msg[7] = crc >> 8;
  writeByteArray(msg, sizeof(msg));
}

void Communication::pri_valveActionHandler() {
  if (m_valve == nullptr)
    return;
  switch (m_stMsg.action) {
  case ACTION_SET_DELAY:
    pri_valvePulseHandler();
    break;
  case ACTION_TURN_ON:
    pri_valveTurnOnHandler();
    break;
  case ACTION_TURN_OFF:
    pri_valveTurnOffHandler();
    break;
  default:
    break;
  }
}

void Communication::pri_valvePulseHandler() {
  uint16_t delayTime = 0;
  delayTime = m_stMsg.params[1] << 8 | m_stMsg.params[0]; // Combine two bytes into delay value
  m_valve->setBlastDelay(delayTime);
  replyACK();
}

void Communication::pri_valveTurnOnHandler() {
  m_valve->turnOn();
  replyACK();
}

void Communication::pri_valveTurnOffHandler() {
  m_valve->turnOff();
  replyACK();
}
