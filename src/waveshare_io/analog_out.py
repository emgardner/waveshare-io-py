from typing import List, Union
from pydantic import BaseModel
import pymodbus.client as ModbusClient
from enum import IntEnum
from waveshare_io.common import Baudrate, Parity


class InputRegisterBases(IntEnum):
    InputChannels = 0x0000

class HoldingRegisterBases(IntEnum):
    Outputs = 0x0000
    UartParameters = 0x2000
    DeviceAddress = 0x4000
    SoftwareVersion = 0x8000

class Channel(IntEnum):
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3
    CHANNEL_5 = 4
    CHANNEL_6 = 5
    CHANNEL_7 = 6
    CHANNEL_8 = 7

class ChannelStatus(BaseModel):
    channel_1: float
    channel_2: float
    channel_3: float
    channel_4: float
    channel_5: float
    channel_6: float
    channel_7: float
    channel_8: float

class AnalogIOController:
    def __init__(self, client: ModbusClient.AsyncModbusSerialClient, address: int = 1) -> None:
        self._client = client
        self._address = address

    def set_address(self, address: int) -> None:
        self._address = address

    async def connect(self) -> None:
        await self._client.connect()

    async def set_device_address(self, address: int) -> None:
        if address > 255:
            raise Exception("Invalid Address Requested")
        await self._client.write_register(
            HoldingRegisterBases.DeviceAddress, address, device_id=self._address
        )

    async def set_uart_paramters(self, baudrate: Baudrate, parity: Parity) -> None:
        value = parity << 16 | baudrate
        await self._client.write_register(
            HoldingRegisterBases.UartParameters, value, device_id=self._address
        )

    async def read_software_version(self) -> int:
        response = await self._client.read_holding_registers(
            HoldingRegisterBases.SoftwareVersion, count=1, device_id=self._address
        )
        return response.registers[0]

    async def set_channel(self, channel: Union[Channel, int], value: float) -> None:
        output_channel = 0
        if isinstance(channel, Channel):
            output_channel = channel.value
        else:
            output_channel = channel
        await self._client.write_register(
            HoldingRegisterBases.Outputs + output_channel, int(value / 1000.0)
        )

    async def set_channels(self, values: List[float]) -> None:
        out = [ int(value/1000.0) for value in values ]
        await self._client.write_registers(
            HoldingRegisterBases.Outputs, out
        )

    async def get_channel_values(self) -> List[float]:
        response = await self._client.read_holding_registers(
            HoldingRegisterBases.Outputs,
            count=8
        )
        out = [ value /1000.0  for value in response.registers ]
        return out
