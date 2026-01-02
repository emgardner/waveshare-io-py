from waveshare_io.digital_io import DigitalIOController
import asyncio
from pymodbus.client import AsyncModbusSerialClient

async def main():
    client = AsyncModbusSerialClient(
        port="/dev/tty.usbmodemBCEBA6ABCD1",
        baudrate=9600,
    )
    controller = DigitalIOController(
        client
    )
    await controller.connect()
    print(await controller.read_software_version())
    for i in range(0, 8):
        await controller.set_channel_on(i)
        await asyncio.sleep(.25)
    for i in range(0, 8):
        await controller.set_channel_off(i)
        await asyncio.sleep(.25)

if __name__ == '__main__':
    asyncio.run(main())




