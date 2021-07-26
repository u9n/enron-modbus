import struct
from typing import Iterable, Dict, Union


def iterbits(data: int, amount: int) -> Iterable[bool]:
    """
    Extracts the LSB and return it as a bool.
    Returns an iterable that gives all bits from the LSB to MSB as bools.
    Limits with the amount.
    """
    for i in range(0, amount):
        bit = bool(data & 0x01)
        yield bit
        data = data >> 1


def map_boolean_byte(
    start_register: int,
    amount: int,
    boolean_data: int,
) -> Dict[int, bool]:
    register = start_register
    result = dict()
    for bit in iterbits(boolean_data, amount):
        result[register] = bit
        register += 1

    return result


def map_boolean_response(
    start_register: int, amount: int, boolean_response: bytes
) -> Dict[int, bool]:
    register = start_register
    leftover_amount = amount
    result = dict()
    for _byte in boolean_response:
        if leftover_amount <= 8:
            # just one byte or the last one.
            result.update(map_boolean_byte(register, leftover_amount, _byte))
        else:
            # map a full byte and move on
            result.update(map_boolean_byte(register, 8, _byte))
            register += 8
            leftover_amount -= 8

    return result


def number_of_bytes_containing_booleans(amount_booleans: int):
    boolean_parts = amount_booleans / 8
    rounded = round(boolean_parts)
    if rounded < boolean_parts:
        # we need to round up the the nearest byte to make sure we get it in the
        # response.
        rounded += 1

    return rounded


def get_numeric_value_size(register: int):
    if 3000 < register < 4000:
        # 16 bit integer
        return 2
    elif 5000 < register < 6000:
        # 32 bit integer
        return 4
    elif 7000 < register < 8000:
        # 32 bit float
        return 4
    else:
        raise ValueError(f"{register} is not a numeric register")


def unpack_numeric_data(register: int, data: bytes) -> Union[int, float]:
    if 3000 < register < 4000:
        # 16 bit integer
        return struct.unpack(">h", data)[0]
    elif 5000 < register < 6000:
        # 32 bit integer
        return struct.unpack(">i", data)[0]
    elif 7000 < register < 8000:
        # 32 bit float
        return struct.unpack(">f", data)[0]
    else:
        raise ValueError(f"{register} is not a numeric register")


def pack_numeric_data(register: int, data: Union[int, float]) -> bytes:
    if 3000 < register < 4000:
        # 16 bit integer
        return struct.pack(">h", data)
    elif 5000 < register < 6000:
        # 32 bit integer
        return struct.pack(">i", data)
    elif 7000 < register < 8000:
        # 32 bit float
        return struct.pack(">f", data)
    else:
        raise ValueError(f"{register} is not a numeric register")


def map_numeric_response(
    start_register: int, amount: int, raw_data: bytes
) -> Dict[int, Union[int, float]]:
    data_map: Dict[int, Union[int, float]] = dict()
    # You are not allowed to mix registers in requests and responses so we are sure
    # all the data is the same.
    data_size = get_numeric_value_size(start_register)
    data = [raw_data[i : i + data_size] for i in range(0, len(raw_data), data_size)]
    register = start_register
    for i in range(0, amount):
        data_map[register] = unpack_numeric_data(register, data[i])
        register += 1
    return data_map
