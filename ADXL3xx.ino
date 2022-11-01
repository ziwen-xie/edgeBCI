#include <ArduinoBLE.h>
#include <Arduino_APDS9960.h>
#include "SerialDataExporter.h"

int bufferSizes[] = {255, 3, 2};
SerialDataExporter exporter = SerialDataExporter(Serial, bufferSizes);

#define LED 7
// these constants describe the pins. They won't change:
const int groundpin = 18;             // analog input pin 4 -- ground
const int powerpin = 19;              // analog input pin 5 -- voltage
const int xpin = A3;                  // x-axis of the accelerometer
const int ypin = A2;                  // y-axis
const int zpin = A1;                  // z-axis (only on 3-axis models)

int x_rec = 70;
int y_rec = 70;
int z_rec = 70;

int x_dif = 0;
int y_dif = 0;
int z_dif = 0;

int state = 0;

int sensorPin = A0;
int sensorValue = 0;

//bluetooth
/*
#include <ArduinoBLE.h>

BLEService ledService("180A"); // BLE LED Service

// BLE LED Switch Characteristic - custom 128-bit UUID, read and writable by central
BLEByteCharacteristic switchCharacteristic("2A57", BLERead | BLEWrite);
*/

void setup() {
  // initialize the serial communications:
  Serial.begin(9600);    // initialize serial communication
  /*
  while (!Serial);

  // set LED's pin to output mode
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  digitalWrite(LED_BUILTIN, LOW);         // when the central disconnects, turn off the LED
  digitalWrite(LEDR, HIGH);               // will turn the LED off
  digitalWrite(LEDG, HIGH);               // will turn the LED off
  digitalWrite(LEDB, HIGH);                // will turn the LED off

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy failed!");

    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Nano 33 BLE Sense");
  BLE.setAdvertisedService(ledService);

  // add the characteristic to the service
  ledService.addCharacteristic(switchCharacteristic);

  // add service
  BLE.addService(ledService);

  // set the initial value for the characteristic:
  switchCharacteristic.writeValue(0);

  // start advertising
  BLE.advertise();

  Serial.println("BLE LED Peripheral");
*/
  x_rec = analogRead(xpin);
  y_rec = analogRead(ypin);
  z_rec = analogRead(zpin);
  // Provide ground and power by using the analog inputs as normal digital pins.
  // This makes it possible to directly connect the breakout board to the
  // Arduino. If you use the normal 5V and GND pins on the Arduino,
  // you can remove these lines.
  //pinMode(groundpin, OUTPUT);
  //pinMode(powerpin, OUTPUT);
  //digitalWrite(groundpin, LOW);
  //digitalWrite(powerpin, HIGH);
  pinMode(LED,OUTPUT);
  
  pinMode(sensorPin, INPUT); 
}



void loop() {
  /*
  //bluetooth
  // listen for Bluetooth® Low Energy peripherals to connect:
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());
    digitalWrite(LED_BUILTIN, HIGH);            // turn on the LED to indicate the connection

    // while the central is still connected to peripheral:
    while (central.connected()) {
      // if the remote device wrote to the characteristic,
      // use the value to control the LED:
      if (switchCharacteristic.written()) {
        switch (switchCharacteristic.value()) {   // any value other than 0
          case 01:
            Serial.println("Red LED on");
            digitalWrite(LEDR, LOW);            // will turn the LED on
            digitalWrite(LEDG, HIGH);         // will turn the LED off
            digitalWrite(LEDB, HIGH);         // will turn the LED off

            digitalWrite(LED, HIGH); //turn the NIR on 
            sensorValue = analogRead(sensorPin);
            switchCharacteristic.writeValue(sensorValue);
            

            break;
          case 02:
            Serial.println("Green LED on");
            digitalWrite(LEDR, HIGH);         // will turn the LED off
            digitalWrite(LEDG, LOW);        // will turn the LED on
            digitalWrite(LEDB, HIGH);        // will turn the LED off

            digitalWrite(LED, LOW);  // turn NIR off
            break;
          case 03:
            Serial.println("Blue LED on");
            digitalWrite(LEDR, HIGH);         // will turn the LED off
            digitalWrite(LEDG, HIGH);       // will turn the LED off
            digitalWrite(LEDB, LOW);         // will turn the LED on
            break;
          default:
            Serial.println(F("LEDs off"));
            digitalWrite(LEDR, HIGH);          // will turn the LED off
            digitalWrite(LEDG, HIGH);        // will turn the LED off
            digitalWrite(LEDB, HIGH);         // will turn the LED off
            break;
        }
      }
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
    digitalWrite(LED_BUILTIN, LOW);         // when the central disconnects, turn off the LED
    digitalWrite(LEDR, HIGH);          // will turn the LED off
    digitalWrite(LEDG, HIGH);        // will turn the LED off
    digitalWrite(LEDB, HIGH);         // will turn the LED off
  }

*/
  // print the sensor values:
  x_dif = abs(analogRead(xpin) - x_rec);
  y_dif = abs(analogRead(ypin) - y_rec);
  z_dif = abs(analogRead(zpin) - z_rec);

  x_rec = analogRead(xpin);
  y_rec = analogRead(ypin);
  z_rec = analogRead(zpin);

  //Serial.print(x_dif);
  //Serial.print("\t");
  //Serial.print(y_dif);
  //Serial.print("\t");
  //Serial.print(z_dif);
  //Serial.println();
  sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (5.0 / 1023.0);
  //switchCharacteristic.writeValue(sensorValue);
  Serial.println(voltage);
  exporter.add("x", voltage);  // Export counter1 as a variable named x
  exporter.exportJSON();        // Send the data via Serial
  digitalWrite(LED, HIGH);
  // delay before next reading:
  /*
  if(x_dif > 100 || y_dif > 100 || z_dif >100){
      if(state == 0){
        digitalWrite(LED, HIGH); 
        state = 1;
      }
      else{
        digitalWrite(LED, HIGH); 
        state = 0;
      }
  }
  */
  delay(100);
}





 