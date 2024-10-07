//#include "UnloaderServo.h"
//#include "StarWheelServo.h"
//#include "DebounceInput.h"
//#include "Servo.h"
//Servo myServo;
//HardwareSerial *serial = &Serial1;
//Unloader unloader;
////StarWheelServo sw;
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
//void loop() {
////  if (unloader.unload() != ReadBack_Status::NORMAL) {
////    Serial.println("Unload failed!");
////    unloader.resetError();
////    unloader.init(2);
////    unloader.homing();    
////  }
//  delay(2000); 
//  unloader.getUnloaderPos();
//  delay(2000);
//}





// #include "ST3215_Comm.h"
// #include "Servo.h"
//
// HardwareSerial *serial = &Serial1;  // Use Serial1 or the correct serial port for your hardware setup
// Servo myServo;
//
// int16_t currentPosition = 0;  // Initialize with a starting position
// uint8_t id = 1;  // Example device ID
// uint16_t speed = 3400;  // Example speed
// uint8_t acc = 150;  // Example acceleration
//
// void setup() {
//     Serial.begin(9600);  // Start the debugging serial port
//     while (!Serial) { continue; }  // Wait for the serial port to connect
//     serial->begin(1000000);  // Start the hardware serial port at 1 Mbps
//     myServo.setSerial(serial);  // Assign the serial port to the Servo object
//     // Move to initial position
// //    myServo.goPosByCount(id, currentPosition, speed, acc);  
// //    delay(1000);  // Delay to allow motor to move
// }
// void loop() {
//     // Increment position by 50
//     currentPosition += 512;
//     // Send new position command
//     Serial.print("Sending to position: ");
//     Serial.println(currentPosition);
//     ReadBack_Status status = myServo.goPosByCount(id, currentPosition, speed, acc);  
//     if (status != ReadBack_Status::NORMAL) {
//         Serial.println("Failed to send move command.");
//     }
//     delay(2000);  // Increased delay to ensure the servo has time to move
//     // Read current position
//     if (myServo.getPos(id, currentPosition) == ReadBack_Status::NORMAL) {
//         Serial.print("Current Position: ");
//         Serial.println(currentPosition);
//         Serial.print("---------------------------------");
//     } else {
//         Serial.println("Failed to read position.");
//     }
// }




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
// comm.setServo(&servo);
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
