import logging
import asyncio
import platform
import ast

from aioconsole import ainput
from bleak import BleakClient
from bleak import BleakScanner

# These values have been randomly generated - they must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well

RED_LED_UUID = '13012F01-F8C3-4F4A-A8F4-15CD926DA146'
GREEN_LED_UUID = '13012F02-F8C3-4F4A-A8F4-15CD926DA146'
BLUE_LED_UUID = '13012F03-F8C3-4F4A-A8F4-15CD926DA146'

on_value = bytearray([0x01])
off_value = bytearray([0x00])

RED = False
GREEN = False
BLUE = False

async def GetRGBValue(client):
    val = await client.read_gatt_char(RED_LED_UUID)
    if (val == on_value):
        print('RED ON')
        RED = True
    else:
        print('RED OFF')
        RED = False

    val = await client.read_gatt_char(GREEN_LED_UUID)
    if (val == on_value):
        print('GREEN ON')
        GREEN = True
    else:
        print('GREEN OFF')
        GREEN = False

    val = await client.read_gatt_char(BLUE_LED_UUID)
    if (val == on_value):
        print('BLUE ON')
        BLUE = True
    else:
        print('BLUE OFF')
        BLUE = False

def getValue(on):
    if on:
        return on_value
    else:
        return off_value


async def setColor(client):
    global RED, GREEN, BLUE
    val = await ainput('Enter rgb to toggle red, green and blue LEDs :')
    # val = input('Enter rgb to toggle red, green and blue LEDs :')
    print(val)

    if ('r' in val):
        print("Toggling red")
        RED = not RED
        await client.write_gatt_char(RED_LED_UUID, getValue(RED))
    if ('g' in val):
        print("Toggling green")
        GREEN = not GREEN
        await client.write_gatt_char(GREEN_LED_UUID, getValue(GREEN))
    if ('b' in val):
        print("Toggling blue")
        BLUE = not BLUE
        await client.write_gatt_char(BLUE_LED_UUID, getValue(BLUE))
    await GetRGBValue(client)

async def run():
    global RED, GREEN, BLUE

    print('ProtoStax Arduino Nano BLE LED Peripheral Central Service')
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')

    found = False
    devices = await BleakScanner.discover()
    for d in devices:
        print("Found device with name: {}".format(d.name))
        if d.name is not None and 'Arduino Nano 33 BLE Sense' in d.name:
            print('Found Arduino Nano 33 BLE Sense Peripheral')
            found = True
            async with BleakClient(d.address) as client:
                print(f'Connected to {d.address}')
                await GetRGBValue(client)

                while True:
                    await setColor(client)

    if not found:
        print('Could not find Arduino Nano 33 BLE Sense Peripheral')


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run())
except KeyboardInterrupt:
    print('\nReceived Keyboard Interrupt')
finally:
    print('Program finished')

