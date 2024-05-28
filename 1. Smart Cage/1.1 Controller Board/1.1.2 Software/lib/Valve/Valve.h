#ifndef VALVE_H
#define VALVE_H
#include <Arduino.h>

class Valve
{
public:
  void init(uint8_t pin);
  void turnOn();
  void turnOff();
  void blast();

private:
  uint8_t m_pin;
};

#endif