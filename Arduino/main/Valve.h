#ifndef VALVE_H
#define VALVE_H
#include <Arduino.h>

class Valve {
public:
  void init(uint8_t pin);
  void turnOn();
  void turnOff();
  void blast();
  void setBlastDelay(unsigned long delay_ms);

private:
  uint8_t m_pin;
  unsigned long m_blastDelay = 200; // Default delay set to 200 ms
};

#endif