#include "Valve.h"

void Valve::init(uint8_t pin)
{
  m_pin = pin;
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

void Valve::turnOn() { digitalWrite(m_pin, HIGH); }
void Valve::turnOff() { digitalWrite(m_pin, LOW); }
void Valve::blast()
{
  this->turnOn();
  delay(200);
  this->turnOff();
}
