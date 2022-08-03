from distutils.command.build import build
from typing import Any, Dict
from pyModbusTCP.client import ModbusClient
import pandas as pd
import re as regex

from opcua import ua, Server, Node

class EdgeDevice():
    bytesRead = 0
    registerValues = dict()
    excelData = pd.DataFrame()
    df = pd.DataFrame()


    def initializeFromLegacy(self):
        types = opcuaServer.get_node(ua.ObjectIds.BaseObjectType)
        ATV72TYPE: Node = types.add_object_type(0, "ATV72")

        self.excelData = pd.read_excel('ATV71_communication_parameters_EN_V5.7_IE67.xls', 1)
        self.df = pd.DataFrame(self.excelData)

        for col in self.df.columns:
            ATV72TYPE.add_property(0, col, "")

        ATV72TYPE.set_modelling_rule(True)

        print("Device info read. Reading the registers")

        for i in range(0, noEntriesInitialized):
            print("Reading " + str(i) + "/" + str(noEntriesInitialized))
            registerString = self.df.at[i, 'Logic\naddress']
            if registerString != '-':
                numbers = regex.findall(r'\d+', registerString)
                registerAddress = (int)(numbers[numbers.__len__() - 1])
                value = modbusClient.read_holding_registers(registerAddress)
                self.bytesRead = self.bytesRead + 2
                self.registerValues[registerAddress] = value
                atv72object: Node = opcuaObjects.add_object(0, self.df.at[i, 'Name'], ATV72TYPE)
                atv72object.add_variable(0, 'RegisterValue', value)

                for prop in ATV72TYPE.get_properties():
                    p: Node = prop
                    string = str(p.get_display_name())
                    string = string.split(':')
                    string = string[string.__len__() - 1].split(')')

                    atv72object.add_property(0, string[0], str(self.df.at[i, string[0]]))

        print("Registers read")

    def queryLegacy(self):
        for i in range(0, noEntriesInitialized):
            registerString = self.df.at[i, 'Logic\naddress']
            if registerString != '-':
                numbers = regex.findall(r'\d+', registerString)
                registerAddress = (int)(numbers[numbers.__len__() - 1])
                value = modbusClient.read_holding_registers(registerAddress)
                if value != self.registerValues[registerAddress]:
                    print("new value for register " + str(registerAddress) + ". from " + str(self.registerValues[registerAddress]) + " to " + str(value))
                    self.registerValues[registerAddress] = value
                    self.bytesRead = self.bytesRead + 2

                    atv72object = opcuaObjects.get_child(self.df.at[i, 'Name'])
                    valueNode = atv72object.get_child("RegisterValue")
                    valueNode.set_value(value)

                    #atv72object: Node = opcuaObjects.add_object(0, df.at[i, 'Name'], ATV72TYPE)
                    #atv72object.add_variable(0, 'RegisterValue', value)
                    
                    opcuaServer.export_xml([valueNode], "opcuanodes.xml")


modbusClient = ModbusClient('localhost', 12000)
print("Starting Edge device")
modbusClient.open()
# parse the xls into opc ua object types
opcuaServer = Server()

opcuaObjects = opcuaServer.get_objects_node()
noEntriesInitialized = 100
noEntriesUpdated = 931
#opcuaServer.export_xml(opcuaObjects.get_referenced_nodes(), "opcuanodes.xml")

try:
    opcuaServer.start()

    edgeDevice = EdgeDevice()
    edgeDevice.initializeFromLegacy()
    while True:
        edgeDevice.queryLegacy()
except Exception as e:
    print(e)
    opcuaServer.stop()
    print("Stopping Edge device")
    modbusClient.close()
