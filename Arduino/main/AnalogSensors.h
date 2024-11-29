#ifndef ANALOG_SENSORS_H
#define ANALOG_SENSORS_H

#include "Define.h"
#include <Arduino.h>

class AnalogSensors {
private:
  uint8_t m_num_sensors{0};
  const uint8_t *m_sensors_array_ptr;

public:
  void init(const uint8_t num_of_sensors, const uint8_t *sensors_array);
  uint8_t getValue(uint8_t index) const;
};

#endif
