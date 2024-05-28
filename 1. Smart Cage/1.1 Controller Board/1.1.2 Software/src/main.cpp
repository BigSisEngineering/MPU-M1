#include "AnalogSensors.h"
#include "Communication.h"
#include "Define.h"
#include "Servo.h"
#include "StarWheelServo.h"
#include "UnloaderServo.h "
#include "Valve.h"
/* ---------------------------------------------------------------------------------------------- */
#include <Arduino.h>

static Servo          servo;
static Unloader       unloader;
static StarWheelServo star_wheel;
static AnalogSensors  sensors;
static Communication  comm;
static Valve          valve;

static const uint8_t POSITIONER_PIN_UNLOADER   = 16;
static const uint8_t POSITIONER_PIN_STAR_WHEEL = GPIO_OPT3; //! Warning: Cage0x0014 is using GPIO_OPT3
static const uint8_t SENSOR_ARRAY[4]{ 18, 19, 20, 21 };

void setup()
{
  // Serial setup
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1);

  // Pass servo Serial bus
  servo.setSerial(&Serial1);

  // Valve
  valve.init(GPIO_SIG5);

  // Set Communication
  comm.init(&Serial);
  comm.setStarWheelServo(&star_wheel);
  comm.setUnloader(&unloader);
  comm.setSensors(&sensors);

  // Create unloader
  unloader.init(POSITIONER_PIN_UNLOADER);
  unloader.setServo(&servo);

  // Create Starwheel
  star_wheel.init(POSITIONER_PIN_STAR_WHEEL);
  star_wheel.setServo(&servo);
  star_wheel.setValve(&valve);
  star_wheel.setCW();

  // sensors
  sensors.init(4, SENSOR_ARRAY);
}

void loop()
{
  comm.update();
}
