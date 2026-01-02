from enum import IntEnum


class Baudrate(IntEnum):
    B4800 = 0x00
    B9600 = 0x01
    B19200 = 0x02
    B38400 = 0x03
    B57600 = 0x04
    B115200 = 0x05
    B128000 = 0x06
    B256000 = 0x07


class Parity(IntEnum):
    NoParity = 0x00
    Even = 0x01
    Odd = 0x02
