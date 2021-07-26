def make_crc16_table():

    result = []
    initial = 0x0000
    for byte in range(256):
        crc = initial
        for _ in range(8):
            if (byte ^ crc) & 0x0001:
                crc = (crc >> 1) ^ 0xa001
            else: crc >>= 1
            byte >>= 1
        result.append(crc)
    return result

crc16_table = make_crc16_table()


def calculate_crc(data: bytes) -> bytes:
    """
    The difference between modbus's crc16 and a normal crc16
    is that modbus starts the crc value out at 0xffff.
    """
    initial = 0xffff
    crc = initial
    for _byte in data:
        idx = crc16_table[(crc ^ _byte) & 0xff]
        crc = ((crc >> 8) & 0xff) ^ idx
    swapped = ((crc << 8) & 0xff00) | ((crc >> 8) & 0x00ff)
    return swapped.to_bytes(2, 'big')


def crc_is_valid(data: bytes, check: bytes):
    """
    """
    return calculate_crc(data) == check
