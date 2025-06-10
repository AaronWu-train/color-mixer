import time
import RPi.GPIO as GPIO
import board
import busio
from adafruit_tcs34725 import TCS34725

i2c = busio.I2C(board.SCL, board.SDA)
sensor = TCS34725(i2c)
sensor.gain = 60
sensor.integration_time = 100

# ——— LED設定 ———
LED_PIN = 17  # BCM17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)  # LOW＝關燈


async def readSensorRawRGB():
    r, g, b, c = sensor.color_raw
    return r, g, b, c


def main():
    try:
        while True:
            raw = readSensorRawRGB()
            print(f"Raw RGBC: {raw}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
