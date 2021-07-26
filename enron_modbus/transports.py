from typing import *
import serial  # type: ignore
import attr
import structlog

LOG = structlog.get_logger()


class EnronModbusTransport(Protocol):
    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def send(self, data: bytes):
        ...

    def recv(self, size: int):
        ...


class TransportException(Exception):
    """General Transport Exception"""


class NotConnectedError(TransportException):
    """Transport is not connected"""


@attr.s(auto_attribs=True)
class SerialTransport:
    port: str
    baudrate: int
    timeout: int = attr.ib(default=5)
    extra_settings: Dict = attr.ib(factory=dict)
    serial_port: Optional[serial.Serial] = attr.ib(init=False, default=None)

    def connect(self) -> None:
        LOG.debug("Opening serial port", serial_port=self.port, baudrate=self.baudrate)
        self.serial_port = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            **self.extra_settings,
        )

    def disconnect(self) -> None:
        if self.serial_port:
            LOG.debug("Closing serial port", serial_port=self.port)
            self.serial_port.close()

        self.serial_port = None

    def send(self, data: bytes) -> None:
        if not self.serial_port:
            raise NotConnectedError(f"{self} is not connected")
        LOG.debug("Sending serial data", data=data)
        self.serial_port.write(data)

    def recv(self, size: int) -> bytes:
        if not self.serial_port:
            raise NotConnectedError(f"{self} is not connected")
        LOG.debug(f"Reading serial data", size=size)
        result = self.serial_port.read(size)
        LOG.debug(f"Received data", data=result)
        return result

