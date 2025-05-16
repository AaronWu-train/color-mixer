#include <Wire.h>
#include "Adafruit_TCS34725.h"

Adafruit_TCS34725 tcs = Adafruit_TCS34725(
    TCS34725_INTEGRATIONTIME_700MS, 
    TCS34725_GAIN_1X);

void setup() {
  Serial.begin(9600);
  if (tcs.begin()) {
    Serial.println("TCS34725 found!");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
}

void loop() {
  uint16_t r, g, b, c;
  tcs.getRawData(&r, &g, &b, &c);
  float colorTemp = tcs.calculateColorTemperature(r, g, b);
  float lux = tcs.calculateLux(r, g, b);

  Serial.print("R: "); Serial.print(r);
  Serial.print(" G: "); Serial.print(g);
  Serial.print(" B: "); Serial.print(b);
  Serial.print(" C: "); Serial.print(c);
  Serial.print(" Color Temp: "); Serial.print(colorTemp);
  Serial.print(" K Lux: "); Serial.println(lux);
  
  delay(1000);
}
