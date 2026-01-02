from waveshare_io.analog_out import AnalogOutController
from waveshare_io.analog_in import AnalogInController
import asyncio
from pymodbus.client import AsyncModbusSerialClient


async def main():
    out_client = AsyncModbusSerialClient(
        port="/dev/tty.usbmodemBCEBA6ABCD3",
        baudrate=9600,
    )
    out_controller = AnalogOutController(out_client)
    in_client = AsyncModbusSerialClient(
        port="/dev/tty.usbmodemBCEBA6ABCD5",
        baudrate=9600,
    )
    in_controller = AnalogInController(in_client)
    await out_controller.connect()
    await in_controller.connect()
    print(await out_controller.read_software_version())
    print(await in_controller.read_software_version())
    for i in range(0, 10000, 100):
        await out_controller.set_channels([i / 1000.0 for _ in range(0, 8)])
        print(await in_controller.read_channels())
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
