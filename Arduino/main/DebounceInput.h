#ifndef DEBOUNCE_INPUT_H
#define DEBOUNCE_INPUT_H

#include <Arduino.h>

inline bool debounceDigitalRead(uint8_t pin, bool normal_high = false)
{
  uint32_t status = normal_high ? (0xFFFFFFFF) : (0); // will read it 32 times
  for (uint8_t ctn = 0; ctn < sizeof(status) * 8; ctn++)
  {
    status = (status << 1) | (digitalRead(pin)); // if read 32 times 1, status will become 0xFFFFFFFF
  }
  if (normal_high)
    return status == 0;
  else
    return (status == 0xFFFFFFFF);
}
#endif
