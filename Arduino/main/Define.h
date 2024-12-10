#ifndef DEFINE_H
#define DEFINE_H

// Motor ID
#define ID_STAR_WHEEL_MOTOR 1
#define ID_UNLOADER_MOTOR 2

// Serial Constant
#define ST3215_SERIAL_BAUDRATE 1000000

// GPIO
#define GPIO_OPT1 15
#define GPIO_OPT2 14
#define GPIO_OPT3 16
#define GPIO_OPT4 10
#define GPIO_SIG1 A0
#define GPIO_SIG2 A1
#define GPIO_SIG3 A2
#define GPIO_SIG4 A3
#define GPIO_SIG5 4
#define GPIO_SIG6 5
#define GPIO_SPARE1 2
#define GPIO_SPARE2 3
#define GPIO_SPARE3 6
#define GPIO_SPARE4 7
#define GPIO_SPARE5 8
#define GPIO_SPARE6 9

// Sensors
#define MAX_NUM_OF_SENSOR 6

// Motor torque
#define MAX_LOAD 950

enum class ReadBack_Status {
  OVERLOAD = 0,
  ERROR,
  TIMEOUT,
  NORMAL,
  OUT_OF_INDEX,
  WRONG_CRC,
  HEADER_L_INCORRECT,
  NO_SERIAL,
  IDLE,
  NOT_INIT,
  NOT_TRIGGERED,
};

inline unsigned int getReadback(ReadBack_Status status) {
  switch (status) {
  case ReadBack_Status::OVERLOAD:
    return (0);
    break;
  case ReadBack_Status::ERROR:
    return (1);
    break;
  case ReadBack_Status::TIMEOUT:
    return (2);
    break;
  case ReadBack_Status::NORMAL:
    return (3);
    break;
  case ReadBack_Status::OUT_OF_INDEX:
    return (4);
    break;
  case ReadBack_Status::WRONG_CRC:
    return (5);
    break;
  case ReadBack_Status::HEADER_L_INCORRECT:
    return (6);
    break;
  case ReadBack_Status::NO_SERIAL:
    return (7);
    break;
  case ReadBack_Status::IDLE:
    return (8);
    break;
  case ReadBack_Status::NOT_INIT:
    return (9);
    break;
  case ReadBack_Status::NOT_TRIGGERED:
    return (5);
    break;
  }
};

#endif
