import attr
from typing import *
import structlog
from enron_modbus import messages, state, utils
from enron_modbus.transports import EnronModbusTransport
from enron_modbus.connection import EnronModbusConnection


LOG = structlog.get_logger()

MINIMAL_REQUEST_SIZE = 5


@attr.s(auto_attribs=True)
class EnronModbusClient:

    transport: EnronModbusTransport
    connection: EnronModbusConnection = attr.ib(factory=EnronModbusConnection)

    def connect(self):
        LOG.info("Client connecting", client=self)
        self.transport.connect()

    def disconnect(self):
        LOG.info("Client disconnecting", client=self)
        self.transport.disconnect()

    def read_booleans(
        self, slave_address: int, start_register: int, amount: int
    ) -> Dict[int, bool]:
        """
        Get all booleans and return them as a dict with the register as key.
        """
        req = messages.BooleanReadRequest(slave_address, start_register, amount)
        read_size = MINIMAL_REQUEST_SIZE + utils.number_of_bytes_containing_booleans(amount)
        response = self.make_request(req, read_size)
        data = utils.map_boolean_response(start_register, amount, response.raw_data)
        return data

    def read_boolean(self, slave_address: int, register: int) -> bool:
        """
        Just read one boolean
        """
        return self.read_booleans(slave_address, register, 1)[register]

    def write_boolean(self, slave_address: int, register: int, value: bool) -> None:
        """
        Set a boolean value
        0xff00 = True, 0x0000 = False
        """
        req = messages.BooleanWriteRequest(slave_address, register, value)
        read_size = 8
        self.make_request(req, read_size)

    def read_numerics(
        self, slave_address: int, start_register: int, amount: int
    ) -> Dict[int, Union[int, float]]:
        """
        Get all numerics and return them as a dict with the register as key.
        """
        # TODO: should we limit the read to registers that are numeric?
        req = messages.NumericReadRequest(slave_address, start_register, amount)
        read_size = (
            MINIMAL_REQUEST_SIZE
            + amount * utils.get_numeric_value_size(start_register)
        )
        response = self.make_request(req, read_size)
        data = utils.map_numeric_response(start_register, amount, response.raw_data)
        return data

    def read_numeric(self, slave_address: int, register: int) -> Union[int, float]:
        """
        Just read one numeric
        """
        return self.read_numerics(slave_address, register, amount=1)[register]

    def write_numeric(self, slave_address: int, register: int, value: Union[int, float]):
        """
        Write a numeric value
        """
        req = messages.NumericWriteRequest(slave_address, register, value)
        read_size = 6 + utils.get_numeric_value_size(register)
        self.make_request(req, read_size)

    def read_history(self, slave_address: int, table: int, index: int) -> bytes:
        """
        Read a history entry
        Uses function code 0x03
        """
        req = messages.HistoryRequest(slave_address, table, index)
        response = self.make_request(req, approx_data_size=MINIMAL_REQUEST_SIZE)
        return response.raw_data

    def make_request(self, request, approx_data_size: int = MINIMAL_REQUEST_SIZE):
        LOG.info("Sending read request", request=request)
        to_send = self.connection.send(request)
        self.transport.send(to_send)
        self.connection.receive_data(self.transport.recv(approx_data_size))
        response = self.next_event()
        LOG.info("Received read response", response=response)
        return response

    def next_event(self):
        """"""

        while True:
            # If we already have a complete event buffered internally, just
            # return that. Otherwise, read some data, add it to the internal
            # buffer, and then try again.
            event = self.connection.next_event()
            if event is state.NEED_DATA:
                data_in_buffer = len(self.connection.buffer)
                message_data_length = self.connection.buffer[2]
                needed_data = (
                    message_data_length + MINIMAL_REQUEST_SIZE - data_in_buffer
                )
                LOG.info(
                    "More data needed",
                    remaining_data=needed_data,
                )
                self.connection.receive_data(self.transport.recv(needed_data))
                continue
            return event
