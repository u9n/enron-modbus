from enron_modbus.client import EnronModbusClient
from enron_modbus.transports import SerialTransport

transport = SerialTransport(port="/dev/tty.usbserial", baudrate=9600)
client = EnronModbusClient(transport=transport)
client.connect()
print(client.read_numeric(1, 3701))
print(client.read_numeric(1, 3702))
print(client.read_numeric(1, 3703))

print(client.read_history(1, 701, 0))
client.disconnect()

