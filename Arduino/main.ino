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

static const uint8_t POSITIONER_PIN_UNLOADER   = 7;
/**
* Use below for 12V sensor
*/
// static const uint8_t POSITIONER_PIN_STAR_WHEEL = GPIO_OPT4; //old board

/**
* Use below for 5v sensor
*/
static const uint8_t POSITIONER_PIN_STAR_WHEEL = GPIO_SIG6; // new board

static const uint8_t SENSOR_ARRAY[4]{ 18, 19, 20, 21 };

void setup()
{
  // Serial setup
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1);

  // Pass servo Serial bus
  servo.setSerial(&Serial1);

  // Valve
  valve.init(GPIO_OPT1); //new board
  // valve.init(GPIO_SIG5);// old Board

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


