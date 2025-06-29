import RPi.GPIO as GPIO
import asyncio
from time import time

pump_index = [17, 22, None, 23, 24, 27]  # GPIO pins for pumps
pump_real_pin = [11, 15, None, 16, 18, 13]  # Real GPIO pins for pumps

motor_index = 25
motor_on = False  # Active LOW

pump_on = [False for _ in range(6)]  # Active LOW

GPIO.setmode(GPIO.BCM)
for pin in pump_index:
    if pin is not None:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Set all pumps to OFF initially

GPIO.setup(motor_index, GPIO.OUT)
GPIO.output(motor_index, GPIO.HIGH)  # Set motor to OFF initially


async def startPump(index, time):
    print("Started", index, time)

    # 底下 motor
    GPIO.output(motor_index, GPIO.LOW)
    global motor_on
    motor_on = True

    index = int(index) - 1  # Convert to zero-based index
    GPIO.output(pump_index[index], GPIO.LOW)
    pump_on[index] = True
    await asyncio.sleep(time)
    GPIO.output(pump_index[index], GPIO.HIGH)
    pump_on[index] = False


async def haltPumpAll():
    for pin in pump_index:
        if pin is not None:
            GPIO.output(pin, GPIO.HIGH)
    for i in range(len(pump_on)):
        pump_on[i] = False

    global motor_on
    GPIO.output(motor_index, GPIO.HIGH)
    motor_on = False


async def haltPump(index):
    GPIO.output(pump_index[index], GPIO.HIGH)
    pump_on[index] = False

    global motor_on
    GPIO.output(motor_index, GPIO.HIGH)
    motor_on = False


async def getPumpStat(index):
    return pump_on[index]


if __name__ == "__main__":
    asyncio.run(startPump(1, 5))
