#include "AnalogSensors.h"

void AnalogSensors::init(const uint8_t num_of_sensors, const uint8_t *sensors_array)
{
  m_num_sensors       = num_of_sensors;
  m_sensors_array_ptr = sensors_array;
}

uint8_t AnalogSensors::getValue(uint8_t index) const
{
  if (index > m_num_sensors - 1) return 0;
  int     val = analogRead(m_sensors_array_ptr[index]);
  uint8_t res = (map(val,
                     0,
                     1023,
                     1,
                     255));
  return res;
}