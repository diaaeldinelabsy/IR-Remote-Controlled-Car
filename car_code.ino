#include <Arduino.h>
#include "IRremote.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <AFMotor.h>

// Setup 4 DC motors on motor shield
AF_DCMotor motor1(1, MOTOR12_1KHZ); 
AF_DCMotor motor2(2, MOTOR12_1KHZ); 
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

// IR receiver pin
#define RECV_PIN 44
IRrecv irReceiver(RECV_PIN);
decode_results results;

// OLED display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SCREEN_ADDRESS 0x3C 
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

uint32_t last_decodedRawData = 0;

// Functions I’ll be using
void forward(void);
void left(void);
void right(void);
void back(void);
void halt(void);
void displayCommands_IR(void);
void controlMotors_IR(void);
void displayMessage(const char* message1, const char* message2);

void setup() {
  irReceiver.enableIRIn();  // turn on IR receiver

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    for (;;); // stay stuck if screen not found
  }

  // clear and setup OLED
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.display();
}

void loop() {
  if (irReceiver.decode()) {
    controlMotors_IR();     // move car
    displayCommands_IR();   // show stop info
    irReceiver.resume();    // wait for next button
  }
}

// car goes forward
void forward() {
  motor1.setSpeed(100);
  motor1.run(FORWARD); 
  motor2.setSpeed(100);
  motor2.run(FORWARD); 
  motor3.setSpeed(100);
  motor3.run(FORWARD); 
  motor4.setSpeed(100);
  motor4.run(FORWARD); 
}

// car goes backward
void back() {
  motor1.setSpeed(100);
  motor1.run(BACKWARD); 
  motor2.setSpeed(100);
  motor2.run(BACKWARD); 
  motor3.setSpeed(100);
  motor3.run(BACKWARD); 
  motor4.setSpeed(100);
  motor4.run(BACKWARD); 
}

// car turns left
void left() {
  motor1.setSpeed(100);
  motor1.run(BACKWARD); 
  motor2.setSpeed(100);
  motor2.run(FORWARD); 
  motor3.setSpeed(100);
  motor3.run(FORWARD);  
  motor4.setSpeed(100);
  motor4.run(BACKWARD);  
}

// car turns right
void right() {
  motor1.setSpeed(100);
  motor1.run(FORWARD); 
  motor2.setSpeed(100);
  motor2.run(BACKWARD); 
  motor3.setSpeed(100);
  motor3.run(BACKWARD); 
  motor4.setSpeed(100);
  motor4.run(FORWARD); 
} 

// stop all motors
void halt() {
  motor1.setSpeed(0);
  motor1.run(RELEASE);
  motor2.setSpeed(0);
  motor2.run(RELEASE); 
  motor3.setSpeed(0);
  motor3.run(RELEASE);
  motor4.setSpeed(0);
  motor4.run(RELEASE);
}

// check IR button and show messages
void displayCommands_IR() {
  switch (irReceiver.decodedIRData.decodedRawData) {
    case 0xF708FB04: // POWER
      displayMessage("HELLO", "EMT 2461");
      break;
    case 0xEE11FB04: // 1
      displayMessage("This is:", "State St");
      break;
    case 0xED12FB04: // 2
      displayMessage("Next Stop:", "Lemon Ave");
      break;
    case 0xEC13FB04: // 3
      displayMessage("This is:", "Lemon Ave");
      break;
    case 0xEB14FB04: // 4
      displayMessage("Next Stop:", "Main St");
      break;
    case 0xEA15FB04: // 5
      displayMessage("This is:", "Main St");
      break;
    case 0xE916FB04: // 6
      displayMessage("Next Stop:", "Court St");
      break;
    case 0xE817FB04: // 7
      displayMessage("This is:", "Court St");
      break;
    case 0xE718FB04: // 8
      displayMessage("Next Stop:", "State St");
      break;
    default:
      break;
  }
  last_decodedRawData = irReceiver.decodedIRData.decodedRawData;
}

// check IR button and move car
void controlMotors_IR() {
  switch (irReceiver.decodedIRData.decodedRawData) {
    case 0xBF40FB04:  // forward
      forward();
      break;
    case 0xF906FB04:  // right
      right();
      break;
    case 0xBE41FB04:  // back
      back();
      break;
    case 0xF807FB04:  // left
      left();
      break;
    case 0xBB44FB04:  // stop
      halt();
      break;
    default:
      break;
  }
}

// print to OLED screen
void displayMessage(const char* message1, const char* message2) {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(2);
  display.print(message1);

  display.setCursor(0, 20);
  display.setTextSize(2);
  display.print(message2);

  display.setCursor(30, 45);
  display.setTextSize(2);
  display.print("68 ");
  display.drawCircle(display.getCursorX(), 44, 2, SSD1306_WHITE);
  display.setCursor(display.getCursorX() + 4, 45);
  display.print("F");

  display.display();
}
