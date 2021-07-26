import attr
import structlog
from enron_modbus import state, messages
from typing import *


LOG = structlog.get_logger()


class Encodeable(Protocol):
    def to_bytes(self) -> bytes:
        ...


@attr.s(auto_attribs=True)
class EnronModbusConnection:
    buffer: bytearray = attr.ib(factory=bytearray)
    connection_state: state.EnronModbusState = attr.ib(factory=state.EnronModbusState)

    def send(self, msg: Encodeable):
        self.connection_state.process_message(msg)
        return msg.to_bytes()

    def receive_data(self, data: bytes):
        """
        Receive data in the buffer. After adding data to the buffer one should call
         `next_event`
        """
        if data:
            self.buffer += data
            LOG.debug("Received data in connection data buffer", data=data)

    def next_event(self) -> Any:
        try:
            if self.connection_state.current_state == state.AWAITING_RESPONSE:
                msg = messages.StandardResponseFactory.make_response_from_bytes(
                    self.buffer
                )
            elif self.connection_state.current_state == state.AWAITING_HISTORY_RESPONSE:
                msg = messages.HistoryResponse.from_bytes(self.buffer)
            else:
                raise RuntimeError("cant handle this data.")
            self.connection_state.process_message(msg)
            # clear buffer
            self.buffer = bytearray()
            return msg
        except messages.EnronModbusParsingException as e:
            LOG.debug(
                "Unable to parse buffer as response message. Requesting more data",
                buffer=self.buffer,
            )
            return state.NEED_DATA
