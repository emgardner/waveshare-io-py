from typing import List, Union
from pydantic import BaseModel
import pymodbus.client as ModbusClient
from enum import IntEnum
from waveshare_io.common import Baudrate, Parity


class InputRegisterBases(IntEnum):
    InputChannels = 0x0000


class HoldingRegisterBases(IntEnum):
    ChannelTypes = 0x1000
    UartParameters = 0x2000
    DeviceAddress = 0x4000
    SoftwareVersion = 0x8000


class ChannelType(IntEnum):
    VOLTAGE_0_10V = 0x0000
    VOLTAGE_2_10V = 0x0001
    CURRENT_0_20MA = 0x0002
    CURRENT_4_20MA = 0x0003
    ADC_OUTPUT = 0x0004


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


class AnalogInController:
    def __init__(
        self,
        client: Union[ModbusClient.AsyncModbusSerialClient, str],
        address: int = 1,
        baudrate: int = 9600,
    ) -> None:
        if isinstance(client, ModbusClient.AsyncModbusSerialClient):
            self._client: ModbusClient.AsyncModbusSerialClient = client
        else:
            self._client = ModbusClient.AsyncModbusSerialClient(
                client, baudrate=baudrate
            )
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

    async def set_channel_type(
        self, channel: Union[Channel, int], channel_type: ChannelType
    ) -> None:
        input_channel = 0
        if isinstance(channel, Channel):
            input_channel = channel.value
        else:
            input_channel = channel
        await self._client.write_register(
            HoldingRegisterBases.ChannelTypes + input_channel, channel_type.value
        )

    async def get_channel_type(self, channel: Union[Channel, int]) -> List[ChannelType]:
        input_channel = 0
        if isinstance(channel, Channel):
            input_channel = channel.value
        else:
            input_channel = channel
        response = await self._client.read_holding_registers(
            HoldingRegisterBases.ChannelTypes + input_channel, count=8
        )
        return [ChannelType(value) for value in response.registers]

    async def set_channel_types(self, channel_types: List[ChannelType]) -> None:
        await self._client.write_registers(
            HoldingRegisterBases.ChannelTypes, [ch.value for ch in channel_types]
        )

    async def read_channel(self, channel: Channel) -> float:
        response = await self._client.read_input_registers(
            InputRegisterBases.InputChannels + channel.value
        )
        return response.registers[0] / 1000.0

    async def read_channels(self) -> List[float]:
        out = []
        for i in range(0, 8):
            out.append(await self.read_channel(Channel(i)))
        return out
