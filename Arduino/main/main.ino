//#include "UnloaderServo.h"
//#include "DebounceInput.h"
//#include "Servo.h"
//
//Servo myServo;
//HardwareSerial *serial = &Serial1;
//Unloader unloader;
//
//void setup() {
//  Serial.begin(9600);            // Start serial communication with the PC
//  Serial1.begin(1000000);        // Initialize serial communication with the servo
//  myServo.setSerial(&Serial1);   // Set the serial port for the servo commands
//  unloader.setServo(&myServo);   // Associate the Unloader object with the Servo
//  unloader.init(2);              // Initialize the Unloader with a sensor pin, e.g., 2
//
//  // Perform homing before starting the main loop
//  if (unloader.homing() != ReadBack_Status::NORMAL) {
//    Serial.println("Homing failed!");
//    while(1);  // Stop further execution if homing fails
//  }
//}
//
//void loop() {
//  // Call the unload function repeatedly
//  if (unloader.unload() != ReadBack_Status::NORMAL) {
//    Serial.println("Unload failed!");
////    delay(5000);  // Wait for some time before retrying
//  }
//  delay(1500);  // Wait for the servo to reach the position, adjust as necessary
//}





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
//static const uint8_t POSITIONER_PIN_STAR_WHEEL = GPIO_OPT4; //old board

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
//   valve.init(GPIO_SIG5);// old Board

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
