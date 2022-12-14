# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
import os, sys
import asyncio
import platform
from datetime import datetime
from typing import Callable, Any

import pylsl
from aioconsole import ainput
from bleak import BleakClient, discover, BleakScanner
from pylsl import StreamInfo, StreamOutlet, IRREGULAR_RATE

lsl_data_chunk_size = 1
selected_device = []


class LSLOutletInterface:

    def __init__(self, stream_name):
        info = StreamInfo(stream_name, "Physio", 1, IRREGULAR_RATE, 'float32', 'EdgeBCIID')
        self.outlet = StreamOutlet(info)

    def send_data(self, data_values: [float], timestamps: [float]):

        if len({len(timestamps), len(data_values)}) > 1:
            raise Exception("Data and timestamp lists are the same length.")
        for value, ts in zip(data_values, timestamps):
            self.outlet.push_sample([value], timestamp=ts)
        # with open(self.path, "a+") as f:
        #     if os.stat(self.path).st_size == 0:
        #         print("Created file.")
        #         f.write(",".join([str(name) for name in self.column_names]) + ",\n")
        #     else:
        #         for i in range(len(data_values)):
        #             f.write(f"{times[i]},{delays[i]},{data_values[i]},\n")


class Connection:
    client: BleakClient = None

    def __init__(
            self,
            read_characteristic: str,
            write_characteristic: str,
            lsl_outlet_interface: Callable[[[float], [float]], None],
    ):
        self.read_characteristic = read_characteristic
        self.write_characteristic = write_characteristic
        self.lsl_outlet_interface = lsl_outlet_interface

        self.last_packet_time = datetime.now()
        self.connected = False
        self.connected_device = None

        self.rx_data = []
        self.rx_timestamps = []

    def on_disconnect(self, client: BleakClient, future: asyncio.Future):
        self.connected = False
        # Put code here to handle what happens on disconnet.
        print(f"Disconnected from {self.connected_device.name}!")

    async def cleanup(self):
        if self.client:
            await self.client.stop_notify(read_characteristic)
            await self.client.disconnect()

    async def manager(self):
        print("Starting connection manager.")
        while True:
            if self.client:
                await self.connect()
            else:
                await self.select_device()
                await asyncio.sleep(15.0)

    async def connect(self):
        if self.connected:
            return
        try:
            await self.client.connect()
            self.connected = self.client.is_connected
            if self.connected:
                print(F"Connected to {self.connected_device.name}")
                await self.client.start_notify(
                    self.read_characteristic, self.notification_handler,
                )
                while True:
                    if not self.connected:
                        break
                    await asyncio.sleep(3.0)
            else:
                print(f"Failed to connect to {self.connected_device.name}")
        except Exception as e:
            print(e)

    async def select_device(self):
        print("Bluetooh LE hardware warming up...")
        await asyncio.sleep(2.0)  # Wait for BLE to initialize.
        devices = await BleakScanner.discover()

        print("Please select device [give the device index]: ")
        for i, device in enumerate(devices):
            print(f"{i}: {device.name}")

        # response = -1
        while True:
            response = await ainput("Select device: ")
            try:
                response = int(response.strip())
            except:
                print("Please make valid selection.")

            if response > -1 and response < len(devices):
                break
            else:
                print("Please make valid selection.")

        print(f"Connecting to {devices[response].name}")
        self.connected_device = devices[response]
        self.client = BleakClient(devices[response].address, disconnected_callback=self.on_disconnect)

    def record_time_info(self):
        present_time = pylsl.local_clock()
        self.rx_timestamps.append(present_time)
        self.last_packet_time = present_time

    def clear_received_data_and_timestamps(self):
        self.rx_data.clear()
        self.rx_timestamps.clear()

    def notification_handler(self, sender: str, data: Any):
        self.rx_data.append(int.from_bytes(data, byteorder="big"))
        self.record_time_info()
        if len(self.rx_data) >= lsl_data_chunk_size:
            self.lsl_outlet_interface(self.rx_data, self.rx_timestamps)
            self.clear_received_data_and_timestamps()


#############
# Loops
#############
async def user_console_manager(connection: Connection):
    while True:
        if connection.client and connection.connected:
            input_str = await ainput("Enter string: ")
            bytes_to_send = bytearray(map(ord, input_str))
            await connection.client.write_gatt_char(write_characteristic, bytes_to_send)
            print(f"Sent: {input_str}")
        else:
            await asyncio.sleep(2.0)


async def main():
    while True:
        # YOUR APP CODE WOULD GO HERE.
        await asyncio.sleep(5)


#############
# App Main
#############
read_characteristic = "00001143-0000-1000-8000-00805f9b34fb"
write_characteristic = "00001142-0000-1000-8000-00805f9b34fb"
stream_name = "BLE-EdgeBCI"

if __name__ == "__main__":

    # Create the event loop.
    loop = asyncio.get_event_loop()

    stream_interface = LSLOutletInterface(stream_name)
    connection = Connection(read_characteristic, write_characteristic, stream_interface.send_data)
    try:
        asyncio.ensure_future(connection.manager())
        asyncio.ensure_future(user_console_manager(connection))
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
