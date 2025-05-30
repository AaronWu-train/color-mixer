import RPi.GPIO as GPIO
import asyncio
from time import time

pump_index = [17, 27, 22, 23, 24]  # real 11  # real 13  # real 15  # real 16  # real 18
pump_on = [False for _ in range(5)]  # Active LOW

GPIO.setmode(GPIO.BCM)
for pin in pump_index:
    GPIO.setup(pin, GPIO.OUT)


async def startPump(index, time):
    GPIO.output(pump_index[pin], GPIO.LOW)
    pump_on[index] = True
    await asyncio.sleep(time)
    GPIO.output(pump_index[pin], GPIO.HIGH)
    pump_on[index] = False


async def haltPump(index):
    GPIO.output(pump_index[pin], GPIO.HIGH)
    pump_on[index] = False


async def getPumpStat(index):
    return pump_on[index]
