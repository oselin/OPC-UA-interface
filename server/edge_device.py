from typing import Dict
from pyModbusTCP.client import ModbusClient
import pandas as pd
import re as regex

from opcua import ua, Server, Node

modbusClient = ModbusClient('localhost', 12000)
print("Starting Edge device")
modbusClient.open()

excelData = pd.read_excel('ATV71_communication_parameters_EN_V5.7_IE67.xls', 1)
df = pd.DataFrame(excelData)

print("Device info read. Reading the registers")

# parse the xls into opc ua object types
opcuaServer = Server()
types = opcuaServer.get_node(ua.ObjectIds.BaseObjectType)
ATV72TYPE: Node = types.add_object_type(0, "ATV72")

for col in df.columns:
    ATV72TYPE.add_property(0, col, "")

ATV72TYPE.set_modelling_rule(True)

registerValues = dict()

opcuaObjects = opcuaServer.get_objects_node()

for i in range(0, 931):
    print("Reading " + str(i))
    registerString = df.at[i, 'Logic\naddress']
    if registerString != '-':
        numbers = regex.findall(r'\d+', registerString)
        registerAddress = (int)(numbers[numbers.__len__() - 1])
        value = modbusClient.read_holding_registers(registerAddress)
        registerValues[registerAddress] = value
        atv72object: Node = opcuaObjects.add_object(0, df.at[i, 'Name'], ATV72TYPE)
        atv72object.add_variable(0, 'RegisterValue', value)
        for prop in ATV72TYPE.get_properties():
            p: Node = prop
            string = str(p.get_display_name())
            string = string.split(':')
            string = string[string.__len__() - 1].split(')')

            atv72object.add_property(0, string[0], str(df.at[i, string[0]]))

print("Registers read")

try:
    opcuaServer.start()

    while True:
        for i in range(0, 931):
            registerString = df.at[i, 'Logic\naddress']
            if registerString != '-':
                numbers = regex.findall(r'\d+', registerString)
                registerAddress = (int)(numbers[numbers.__len__() - 1])
                value = modbusClient.read_holding_registers(registerAddress)
                if value != registerValues[registerAddress]:
                    print("new value for register " + str(registerAddress) + ". from " + str(registerValues[registerAddress]) + " to " + str(value))
                    registerValues[registerAddress] = value

                    atv72object: Node = opcuaObjects.add_object(0, df.at[i, 'Name'], ATV72TYPE)
                    atv72object.add_variable(0, 'RegisterValue', value)
                    
                    #opcuaServer.export_xml([atv72object], "opcuanodes.xml")
except:
    opcuaServer.stop()
    print("Stopping Edge device")
    modbusClient.close()
