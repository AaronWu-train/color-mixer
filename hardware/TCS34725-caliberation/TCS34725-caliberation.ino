#include <Wire.h>
#include "Adafruit_TCS34725.h"
// Integration times
#define TCS34725_INTEGRATIONTIME_2_4MS  0xFF   /**<  2.4ms - 1 cycle    - Max Count: 1024  */
#define TCS34725_INTEGRATIONTIME_24MS   0xF6   /**<  24ms  - 10 cycles  - Max Count: 10240 */
#define TCS34725_INTEGRATIONTIME_50MS   0xEB   /**<  50ms  - 20 cycles  - Max Count: 20480 */
#define TCS34725_INTEGRATIONTIME_101MS  0xD5   /**<  101ms - 42 cycles  - Max Count: 43008 */
#define TCS34725_INTEGRATIONTIME_154MS  0xC0   /**<  154ms - 64 cycles  - Max Count: 65535 */
#define TCS34725_INTEGRATIONTIME_700MS  0x00   /**<  700ms - 256 cycles - Max Count: 65535 */

// Gain settings
#define TCS34725_GAIN_1X   0x00   /**< No gain  */
#define TCS34725_GAIN_4X   0x01   /**< 4x gain  */
#define TCS34725_GAIN_16X  0x02   /**< 16x gain */
#define TCS34725_GAIN_60X  0x03   /**< 60x gain */

// Create sensor object with default settings
Adafruit_TCS34725 tcs = Adafruit_TCS34725();

void setup() {
  Serial.begin(9600);

  if (tcs.begin()) {
    Serial.println("TCS34725 found!");
    
    // Optional: Set gain and integration time
    tcs.setIntegrationTime(TCS34725_INTEGRATIONTIME_700MS);
    tcs.setGain(TCS34725_GAIN_1X);
    
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
