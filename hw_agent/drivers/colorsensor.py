import RPi.GPIO as GPIO
import board
import busio
import adafruit_tcs34725

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.enable = False


async def getSensor():
    r, g, b = sensor.color
    color_temp = sensor.color_temperature
    lux = sensor.lux
    return r, g, b, color_temp, lux
