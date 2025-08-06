#include <Arduino.h>
#include "IRremote.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <AFMotor.h>
#include <Servo.h>

// Initialize the 4 motors for our vehicle
AF_DCMotor motor1(1, MOTOR12_1KHZ); 
AF_DCMotor motor2(2, MOTOR12_1KHZ); 
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

// Initialize servo motor
Servo myServo;

// IR receiver setup
#define RECV_PIN 44
IRrecv irReceiver(RECV_PIN);
decode_results results;

// OLED setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SCREEN_ADDRESS 0x3C // Ensure this is the correct I2C address
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Commands will be received as a single character
char command;

// Variable to store the last decodedRawData for the IR sensor
uint32_t last_decodedRawData = 0;

// Servo movement time init
unsigned long lastServoMoveTime = 0;
// Servo starting position
int pos = 0;

// Boolean to turn servo left or right
bool direction = true;

// Function declarations
void servoControl(void);
void forward(void);
void left(void);
void right(void);
void back(void);
void halt(void);
void displayCommands_IR(void);
void controlMotors_IR(void);
void displayMessage(const char* message1, const char* message2);

void setup() {
  // Begin serial communication baud rate
  Serial.begin(9600);
  // Servo attached to pin d10
  myServo.attach(10);
  // Print to serial monitor
  irReceiver.enableIRIn(); // Start the receiver

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Don't proceed, loop forever
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.display();
}

void loop() {
  if (Serial.available() > 0) { 
    command = Serial.read(); 
    halt(); // Initialize with motors stopped
    switch (command) {
      case 'F':  
        forward();
        break;
      case 'B':  
        back();
        break;
      case 'L':  
        left();
        break;
      case 'R':
        right();
        break;
    }
  }
  
  servoControl();
  
  if (irReceiver.decode()) {
    // Follow commands for the IR range
    controlMotors_IR();
    displayCommands_IR();
    
    // Sets IR receiver to accept other signals
    irReceiver.resume();
  }
}

void servoControl() {
  // Servo timer set to turn 180 degrees and then return
  if (millis() - lastServoMoveTime > 10) {
    lastServoMoveTime = millis();
    pos += direction ? 1 : -1;
    // If pos is greater than 180, then set to 0
    if (pos >= 180 || pos <= 0) direction = !direction;
    // Sends range to servo motor
    myServo.write(pos);
  }
}

void forward() {
  // All motors clockwise
  motor1.setSpeed(255);
  motor1.run(FORWARD); 
  motor2.setSpeed(255);
  motor2.run(FORWARD); 
  motor3.setSpeed(255);
  motor3.run(FORWARD); 
  motor4.setSpeed(255);
  motor4.run(FORWARD); 
}

void back() {
  // All motors counterclockwise
  // Speed is slowed down to avoid jerking
  motor1.setSpeed(175);
  motor1.run(BACKWARD); 
  motor2.setSpeed(175);
  motor2.run(BACKWARD); 
  motor3.setSpeed(175);
  motor3.run(BACKWARD); 
  motor4.setSpeed(175);
  motor4.run(BACKWARD); 
}

void left() {
  // Motor1 and motor3 counterclockwise
  motor1.setSpeed(255);
  motor1.run(BACKWARD); 
  motor2.setSpeed(255);
  motor2.run(BACKWARD); 
  motor3.setSpeed(255);
  motor3.run(FORWARD);  
  motor4.setSpeed(255);
  motor4.run(FORWARD);  
}

void right() {
  // Motor1 and motor3 clockwise
  motor1.setSpeed(255);
  motor1.run(FORWARD); 
  motor2.setSpeed(255);
  motor2.run(FORWARD); 
  motor3.setSpeed(255);
  motor3.run(BACKWARD); 
  motor4.setSpeed(255);
  motor4.run(BACKWARD); 
} 

// Could not use stop() for this because stop is a built-in function already
void halt() {
  // Slows motors down to 0
  // Release is supposed to stop movement of the motor in a gentle way
  motor1.setSpeed(0);
  motor1.run(RELEASE);
  motor2.setSpeed(0);
  motor2.run(RELEASE); 
  motor3.setSpeed(0);
  motor3.run(RELEASE);
  motor4.setSpeed(0);
  motor4.run(RELEASE);
}

void displayCommands_IR() {
  // Switch through the different IR frequencies
  switch (irReceiver.decodedIRData.decodedRawData) {
    case 0xEE11FB04:
      // Remote button - 1
      Serial.println("1");
      displayMessage("This is:", "State St");
      break;
    case 0xED12FB04:
      // Remote button - 2
      Serial.println("2");
      displayMessage("Next Stop:", "Lemon Ave");
      break;
    case 0xEC13FB04:
      // Remote button - 3
      Serial.println("3");
      displayMessage("This is:", "Lemon Ave");
      break;
    case 0xEB14FB04:
      // Remote button - 4
      Serial.println("4");
      displayMessage("Next Stop:", "Main St");
      break;
    case 0xEA15FB04:
      // Remote button - 5
      Serial.println("5");
      displayMessage("This is:", "Main St");
      break;
    case 0xE916FB04:
      // Remote button - 6
      Serial.println("6");
      displayMessage("Next Stop:", "Court St");
      break;
    case 0xE817FB04:
      // Remote button - 7
      Serial.println("7");
      displayMessage("This is:", "Court St");
      break;
    case 0xE718FB04:
      // Remote button - 8
      Serial.println("8");
      displayMessage("Next Stop:", "State St");
      break;
    default:
      break;
  }
  last_decodedRawData = irReceiver.decodedIRData.decodedRawData;
}

void controlMotors_IR() {
  switch (irReceiver.decodedIRData.decodedRawData) {
    case 0xBF40FB04:
      // UP button - Forward
      Serial.println("UP - FORWARD");
      forward();
      break;
    case 0xF906FB04:
      // Right button
      Serial.println("RIGHT");
      right();
      break;
    case 0xBE41FB04:
      // Down button - Backward
      Serial.println("DOWN - BACKWARD");
      back();
      break;
    case 0xF807FB04:
      // Left button
      Serial.println("LEFT");
      left();
      break;
    case 0xBB44FB04:
      // OK button (stop)
      Serial.println("OK - STOP");
      halt();
      break;
    default:
      break;
  }
}

// This function simplifies printing messages to the OLED display
// It allows 2 messages to be printed by separating them with a comma
void displayMessage(const char* message1, const char* message2) {
  // First line
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(2);
  display.print(message1);

  // Second line
  display.setCursor(0, 20);
  display.setTextSize(2);
  display.print(message2);
  
  // Third line will display the weather
  display.setCursor(30, 45); // Set cursor position for temperature
  display.setTextSize(2);
  display.print("76 ");
  
  // The following was done to display the degrees icon
  display.drawCircle(display.getCursorX(), 44, 2, SSD1306_WHITE);
  display.setCursor(display.getCursorX() + 4, 45);
  display.print("F");

  // Sends data to the OLED display
  display.display();
}
