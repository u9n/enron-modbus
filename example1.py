from enron_modbus.client import EnronModbusClient
from enron_modbus.transports import SerialTransport

transport = SerialTransport(port="/dev/tty.usbserial", baudrate=9600)
client = EnronModbusClient(transport=transport)
client.connect()
print(client.read_numerics(1, 5160, 6))
print(client.read_numeric(1, 5160))
print(client.read_booleans(1, 1010, 2))
print(client.read_booleans(1, 1010, 33))
print(client.read_boolean(1, 1010))
client.write_boolean(1, 1010, True)
print(client.read_boolean(1, 1010))
client.write_numeric(1, 7001, 46)
print(client.read_numeric(1, 7001))
client.disconnect()

