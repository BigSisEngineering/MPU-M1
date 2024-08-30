//#include "UnloaderServo.h"
//#include "StarWheelServo.h"
//#include "DebounceInput.h"
//#include "Servo.h"
//
//Servo myServo;
//HardwareSerial *serial = &Serial1;
//Unloader unloader;
////StarWheelServo sw;
//
//void setup() {
//  Serial.begin(9600);            // Start serial communication with the PC
//  Serial1.begin(1000000);        // Initialize serial communication with the servo
//  myServo.setSerial(&Serial1);   // Set the serial port for the servo commands
//  unloader.setServo(&myServo);   // Associate the Unloader object with the Servo
//  unloader.init(2);              // Initialize the Unloader with a sensor pin, e.g., 2
////  sw.setServo(&myServo);
////  sw.init(1);
//  
////  sw.homing();
////   Perform homing before starting the main loop
//  if (unloader.homing() != ReadBack_Status::NORMAL) {
//    Serial.println("Homing failed!");
//    while(1);  // Stop further execution if homing fails
//  }
////  if (sw.homing() != ReadBack_Status::NORMAL) {
////    Serial.println("Homing failed!");
////    while(5);  // Stop further execution if homing fails
////  }
//}
//
//void loop() {
//  if (unloader.unload() != ReadBack_Status::NORMAL) {
//    Serial.println("Unload failed!");
////    unloader.resetError();
////    unloader.init(2);
////    unloader.homing();    
//  }
//  
//  delay(2000);  
//}


//void loop() {
//  // Call the unload function and store the result
//  ReadBack_Status status = unloader.unload();
//
////  // Print the status of the unload operation
////  Serial.print("Unload Status: ");
////  switch (status) {
////    case ReadBack_Status::NORMAL:
////      Serial.println("NORMAL");
////      break;
////    case ReadBack_Status::ERROR:
////      Serial.println("ERROR");
////      break;
////    case ReadBack_Status::NO_SERIAL:
////      Serial.println("NO_SERIAL");
////      break;
////    case ReadBack_Status::NOT_INIT:
////      Serial.println("NOT_INIT");
////      break;
////    case ReadBack_Status::OVERLOAD:
////      Serial.println("OVERLOAD");
////      break;
////    case ReadBack_Status::TIMEOUT:
////      Serial.println("TIMEOUT");
////      break;
////    case ReadBack_Status::IDLE:
////      Serial.println("IDLE");
////      break;
////    default:
////      Serial.println("UNKNOWN");
////      break;
////  }
//
////  // Get and print the current load
////  int16_t currentLoad = 0;
////  if (myServo.getLoad(ID_UNLOADER_MOTOR, currentLoad) == ReadBack_Status::NORMAL) {
////    Serial.print("Current Load: ");
////    Serial.println(currentLoad);
////  } else {
////    Serial.println("Failed to read the load.");
////  }
//
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
