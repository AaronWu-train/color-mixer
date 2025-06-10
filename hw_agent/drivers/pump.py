import RPi.GPIO as GPIO
import asyncio
from time import time

pump_index = [17, 22, None, 23, 24, 27]  # GPIO pins for pumps
pump_real_pin = [11, 15, None, 16, 18, 13]  # Real GPIO pins for pumps

pump_on = [False for _ in range(6)]  # Active LOW

GPIO.setmode(GPIO.BCM)
for pin in pump_index:
    GPIO.setup(pin, GPIO.OUT)


async def startPump(index, time):
    index = int(index) - 1  # Convert to zero-based index
    GPIO.output(pump_index[pin], GPIO.LOW)
    pump_on[index] = True
    await asyncio.sleep(time)
    GPIO.output(pump_index[pin], GPIO.HIGH)
    pump_on[index] = False


async def haltPumpAll():
    for pin in pump_index:
        GPIO.output(pin, GPIO.HIGH)
    for i in range(len(pump_on)):
        pump_on[i] = False


async def haltPump(index):
    GPIO.output(pump_index[pin], GPIO.HIGH)
    pump_on[index] = False


async def getPumpStat(index):
    return pump_on[index]
