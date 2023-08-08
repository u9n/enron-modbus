# enron-modbus
A client for Enron Modbus

# Why a separate project?
Some of the work in this library could have been integrated into and already existing 
python modbus library like [riptideio/pymodbus](https://github.com/riptideio/pymodbus).
Comparing the normal use cases for modbus,  Encron Modbus doesn't differ that much but the 
`Operator Event`, `Alarm Event`. `Alarm Acknowledgement` and `History Readout` 
wouldn't really fit in another project

We are mostly interested in the `History Readout` feature and might not implement the 
other special cases unless we need to.


# Example usage

```python
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
```
# About Enron Modbus

Enron Modbus is a modification to the standard Modicon modbus communication protocol. 
It was developed by Enron Corporation. The main differences between the two protocols 
is the numbering of the register addresses, the support of 32 bit registers as well as 
16 bit, and the ability to transmit Event logs and Historical data.

# Data model

Each datatype has its own data table

Data Type | Register Numbers | Data Address 
--- | --- | ---
Boolean | 1001-1999 | 0x03E9-0x07CF
16-bit integer | 3001-3999 | 0x0BB9 to 0x0F9F
32-bit integers | 5001-5999 | 0x1389 to 0x176F
32-bit floats | 7001-7999 | 0x1B59 to 0x1F3F

Difference from normal Modbus is that the register numbers are equal to the data 
address. Offset 0 instead of 1 as in normal Modbus.

# Function codes

Code | Function
--- | ---
0x01 | Read boolean (1xxx)
0x05 | Set single boolean (1xxx)
0x03 | Read numeric (3xxx, 5xxx, 7xxx)
0x06 | Set single numeric (3xxx, 5xxx, 7xxx)

# History Readout

There are two types of history tables, `hourly` and `daily`.

The achives are lists of historical item values with corresponding timestamp.
The items included in the lists are defined in the modbus map.
The tables sizes are also defined in the slave device.

The timestamp is for the end of the capture period (end of hour or end of day)

Each record is given a specific record number.  This number rolls over to zero when 
the table fills up and the device starts writing over old data.  The most current 
record numbers are recoded in variables called the Hourly Index and Daily Index.  
These index variables are typically included in the map as 7000 series numerical 
variables so they can be read.



