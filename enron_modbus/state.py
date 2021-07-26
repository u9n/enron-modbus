import attr
import structlog
from enron_modbus import messages

LOG = structlog.get_logger()


class _SentinelBase(type):
    """
    Sentinel values
     - Inherit identity-based comparison and hashing from object
     - Have a nice repr
     - Have a *bonus property*: type(sentinel) is sentinel
     The bonus property is useful if you want to take the return value from
     next_event() and do some sort of dispatch based on type(event).
     Taken from h11.
    """

    def __repr__(self):
        return self.__name__


def make_sentinel(name):
    cls = _SentinelBase(name, (_SentinelBase,), {})
    cls.__class__ = cls
    return cls


class EnronModbusLocalProtocolError(Exception):
    """A local protocol error occurred."""


IDLE = make_sentinel("IDLE")
AWAITING_RESPONSE = make_sentinel("AWAITING_RESPONSE")
AWAITING_HISTORY_RESPONSE = make_sentinel("AWAITING_HISTORY_RESPONSE")

NEED_DATA = make_sentinel("NEED_DATA")

ENRON_MODBUS_STATE_TRANSITIONS = {
    IDLE: {
        messages.NumericReadRequest: AWAITING_RESPONSE,
        messages.BooleanReadRequest: AWAITING_RESPONSE,
        messages.BooleanWriteRequest: AWAITING_RESPONSE,
        messages.NumericWriteRequest: AWAITING_RESPONSE,
        messages.HistoryRequest: AWAITING_HISTORY_RESPONSE
    },
    AWAITING_RESPONSE: {
        messages.NumericReadResponse: IDLE,
        messages.BooleanReadResponse: IDLE,
        messages.BooleanWriteResponse: IDLE,
        messages.NumericWriteResponse: IDLE
    },
    AWAITING_HISTORY_RESPONSE: {
        messages.HistoryResponse: IDLE
    }
}


@attr.s(auto_attribs=True)
class EnronModbusState:
    current_state: _SentinelBase = attr.ib(default=IDLE)

    def process_message(self, msg):

        self._transition_state(type(msg))

    def _transition_state(self, msg_type):
        try:
            new_state = ENRON_MODBUS_STATE_TRANSITIONS[self.current_state][msg_type]
        except KeyError:
            raise EnronModbusLocalProtocolError(
                f"can't handle frame type {msg_type} when state={self.current_state}"
            )
        old_state = self.current_state
        self.current_state = new_state
        LOG.debug(f"Enron Modbus state transition", old=old_state, new=new_state)
