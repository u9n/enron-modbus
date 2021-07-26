import attr

from enron_modbus import utils
from enron_modbus.crc import calculate_crc, crc_is_valid
from typing import *


@attr.s(auto_attribs=True)
class BooleanWriteRequest:
    FUNCTION_CODE = 0x05
    slave_address: int
    register: int
    value: bool

    def to_bytes(self) -> bytes:
        out = bytearray()
        out.append(self.slave_address)
        out.append(self.FUNCTION_CODE)
        out.extend(self.register.to_bytes(2, "big"))
        if self.value:
            out.extend(b"\xff\x00")
        else:
            out.extend(b"\x00\x00")

        return bytes(out) + calculate_crc(out)


@attr.s(auto_attribs=True)
class BooleanWriteResponse:
    FUNCTION_CODE = 0x05
    slave_address: int
    register: int
    value: bool

    @classmethod
    def from_bytes(cls, source_bytes: bytes):
        data = bytearray(source_bytes)
        slave_address = data.pop(0)
        function_code = data.pop(0)
        if function_code != cls.FUNCTION_CODE:
            raise WrongFuntionCodeError(
                f"Not a BooleanWriteResponse: function code is {function_code!r} "
                f"instead if {cls.FUNCTION_CODE}"
            )
        register = int.from_bytes(data[:2], "big")
        boolean_data = data[2:4]
        if boolean_data == b"\xff\x00":
            value = True
        elif boolean_data == b"\x00\x00":
            value = False
        else:
            raise ValueError(f"Boolean data is not valid: {boolean_data!r}")
        crc = data[4:]

        if not crc_is_valid(source_bytes[:-2], crc):
            raise InvalidCrcError()
        return cls(slave_address, register, value)


@attr.s(auto_attribs=True)
class BooleanReadRequest:
    FUNCTION_CODE = 0x01
    slave_address: int
    start_register: int
    amount: int

    def to_bytes(self):
        out = bytearray()
        out.append(self.slave_address)
        out.append(self.FUNCTION_CODE)
        out.extend(self.start_register.to_bytes(2, "big"))
        out.extend(self.amount.to_bytes(2, "big"))

        return bytes(out) + calculate_crc(out)


class EnronModbusParsingException(Exception):
    """A problem in parsing a message"""


class InvalidLengthError(EnronModbusParsingException):
    """The length of the message is not corresponding to the length described in the message"""


class WrongFuntionCodeError(EnronModbusParsingException):
    """The data does not contain the correct function code"""


class InvalidCrcError(EnronModbusParsingException):
    """CRC is invalid for message"""


class NotEnoughDataError(EnronModbusParsingException):
    """Not enough data to parse the message"""


@attr.s(auto_attribs=True)
class BooleanReadResponse:
    FUNCTION_CODE = 0x01
    slave_address: int
    raw_data: bytearray = attr.ib(factory=bytearray)

    @property
    def length(self):
        return len(self.raw_data)

    @classmethod
    def from_bytes(cls, source_bytes):
        data = bytearray(source_bytes)
        slave_address = data.pop(0)
        function_code = data.pop(0)
        if function_code != cls.FUNCTION_CODE:
            raise WrongFuntionCodeError(
                f"Not a BooleanReadResponse: function code is {function_code!r} "
                f"instead if {cls.FUNCTION_CODE}"
            )
        data_length = data.pop(0)
        if len(data) != data_length + 2:  # data + crc
            raise InvalidLengthError("The message length is not correct")
        raw_data = data[:data_length]
        crc = data[data_length:]

        if not crc_is_valid(source_bytes[:-2], crc):
            raise InvalidCrcError()
        return cls(slave_address, raw_data)


@attr.s(auto_attribs=True)
class NumericReadRequest:
    FUNCTION_CODE = 0x03
    slave_address: int
    start_register: int
    amount: int

    def to_bytes(self) -> bytes:
        out = bytearray()
        out.append(self.slave_address)
        out.append(self.FUNCTION_CODE)
        out.extend(self.start_register.to_bytes(2, "big"))
        out.extend(self.amount.to_bytes(2, "big"))

        return bytes(out) + calculate_crc(out)


@attr.s(auto_attribs=True)
class NumericReadResponse:
    FUNCTION_CODE = 0x03
    slave_address: int
    raw_data: bytearray = attr.ib(factory=bytearray)

    @property
    def length(self):
        return len(self.raw_data)

    @classmethod
    def from_bytes(cls, source_bytes):
        data = bytearray(source_bytes)
        slave_address = data.pop(0)
        function_code = data.pop(0)
        if function_code != cls.FUNCTION_CODE:
            raise WrongFuntionCodeError(
                f"Not a BooleanReadResponse: function code is {function_code!r} "
                f"instead if {cls.FUNCTION_CODE}"
            )
        data_length = data.pop(0)
        if len(data) != data_length + 2:  # data + crc
            raise InvalidLengthError("The message length is not correct")
        raw_data = data[:data_length]
        crc = data[data_length:]

        if not crc_is_valid(source_bytes[:-2], crc):
            raise InvalidCrcError()
        return cls(slave_address, raw_data)


@attr.s(auto_attribs=True)
class NumericWriteRequest:
    FUNCTION_CODE = 0x06
    slave_address: int
    register: int
    value: Union[int, float]

    def to_bytes(self) -> bytes:
        out = bytearray()
        out.append(self.slave_address)
        out.append(self.FUNCTION_CODE)
        out.extend(self.register.to_bytes(2, "big"))
        out.extend(utils.pack_numeric_data(self.register, self.value))
        return bytes(out) + calculate_crc(out)


@attr.s(auto_attribs=True)
class NumericWriteResponse:
    FUNCTION_CODE = 0x06
    slave_address: int
    register: int
    value: Union[int, float]

    @classmethod
    def from_bytes(cls, source_bytes: bytes):
        data = bytearray(source_bytes)
        slave_address = data.pop(0)
        function_code = data.pop(0)
        if function_code != cls.FUNCTION_CODE:
            raise WrongFuntionCodeError(
                f"Not a NumericWriteResponse: function code is {function_code!r} "
                f"instead if {cls.FUNCTION_CODE}"
            )
        register = int.from_bytes(data[:2], "big")
        register_size = utils.get_numeric_value_size(register)
        raw_data = data[2 : 2 + register_size]
        value = utils.unpack_numeric_data(register, raw_data)
        crc = data[2 + register_size :]

        if not crc_is_valid(source_bytes[:-2], crc):
            raise InvalidCrcError()
        return cls(slave_address, register, value)


@attr.s(auto_attribs=True)
class StandardResponseFactory:
    @classmethod
    def make_response_from_bytes(cls, data: bytes):
        try:
            if data[1] == 0x01:
                return BooleanReadResponse.from_bytes(data)
            elif data[1] == 0x03:
                return NumericReadResponse.from_bytes(data)
            elif data[1] == 0x05:
                return BooleanWriteResponse.from_bytes(data)
            elif data[1] == 0x06:
                return NumericWriteResponse.from_bytes(data)
        except IndexError:
            raise NotEnoughDataError()


@attr.s(auto_attribs=True)
class HistoryRequest:
    FUNCTION_CODE = 0x03
    slave_address: int
    table: int
    index: int

    def to_bytes(self) -> bytes:
        out = bytearray()
        out.append(self.slave_address)
        out.append(self.FUNCTION_CODE)
        out.extend(self.table.to_bytes(2, 'big'))
        out.extend(self.index.to_bytes(2, 'big'))

        return bytes(out) + calculate_crc(out)


@attr.s(auto_attribs=True)
class HistoryResponse:
    FUNCTION_CODE = 0x03
    slave_address: int
    raw_data: bytes

    @classmethod
    def from_bytes(cls, source_bytes: bytes):
        data = bytearray(source_bytes)
        slave_address = data.pop(0)
        function_code = data.pop(0)
        if function_code != cls.FUNCTION_CODE:
            raise WrongFuntionCodeError(
                f"Not a HistoryResponse: function code is {function_code!r} "
                f"instead if {cls.FUNCTION_CODE}"
            )
        data_length = data.pop(0)
        raw_data = data[:data_length]
        crc = data[data_length:]

        if not crc_is_valid(source_bytes[:-2], crc):
            raise InvalidCrcError()

        return cls(slave_address, raw_data)
