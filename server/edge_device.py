from atexit import register
from distutils.command.build import build
from typing import Any, Dict
from pyModbusTCP.client import ModbusClient
import pandas as pd
import re as regex

from opcua import ua, Server, Node

class EdgeDevice():
    bytesRead                 = 0
    excelData                 = pd.DataFrame()
    df                        = pd.DataFrame()
    registerAddressToXmlIndex = dict()
    ATV72TPYE: Node
    registerCache             = dict()

    def __init__(self,opcuaServer,modbusClient,opcuaObjects,noEntriesInitialized):
        self.opcuaServer:Server = opcuaServer
        self.modbusClient:ModbusClient = modbusClient
        self.opcuaObjects:Node = opcuaObjects
        self.noEntriesInitialized:int = noEntriesInitialized

    def initializeFromLegacy(self):
        types = self.opcuaServer.get_node(ua.ObjectIds.BaseObjectType)
        self.ATV72TYPE = types.add_object_type(0, "ATV72")

        self.excelData = pd.read_excel('../data/ATV71_communication_parameters_EN_V5.7_IE67.xls', 1)
        self.df = pd.DataFrame(self.excelData)

        for col in self.df.columns:
            self.ATV72TYPE.add_property(0, col, "")

        self.ATV72TYPE.set_modelling_rule(True)

        print("Device info read. Indexing registers")

        for i in range(0, self.noEntriesInitialized):
            print("Reading " + str(i) + "/" + str(self.noEntriesInitialized))
            registerString = self.df.at[i, 'Logic\naddress']
            if registerString != '-':
                numbers = regex.findall(r'\d+', registerString)
                registerAddress = (int)(numbers[numbers.__len__() - 1])
                self.registerAddressToXmlIndex[registerAddress] = i
                '''value = self.modbusClient.read_holding_registers(registerAddress)
                self.bytesRead = self.bytesRead + 2
                self.registerValues[registerAddress] = value
                atv72object: Node = self.opcuaObjects.add_object(0, self.df.at[i, 'Name'], self.ATV72TYPE)
                atv72object.add_variable(0, 'RegisterValue', value)

                for prop in self.ATV72TYPE.get_properties():
                    p: Node = prop
                    string = str(p.get_display_name())
                    string = string.split(':')
                    string = string[string.__len__() - 1].split(')')

                    atv72object.add_property(0, string[0], str(self.df.at[i, string[0]]))'''

    def queryLegacyAndUpdateCache(self):
        for (registerAddress, value) in self.registerCache:
            value = self.modbusClient.read_holding_registers(registerAddress)
            if value != self.registerCache[registerAddress]:
                print("new value for register " + str(registerAddress) + ". from " + str(self.registerCache[registerAddress]) + " to " + str(value))
                self.registerCache[registerAddress] = value
                self.bytesRead = self.bytesRead + 2

                #atv72object = 
                self.getAndUpsertOpcNodeFromRegister(registerAddress)

                #atv72object: Node = opcuaObjects.add_object(0, df.at[i, 'Name'], ATV72TYPE)
                #atv72object.add_variable(0, 'RegisterValue', value)
                
                #self.opcuaServer.export_xml([atv72object.get_child("RegisterValue")], "opcuanodes.xml")

    def readLegacyRegisterWithCaching(self, registerAddress: int):
        if self.registerCache.get(registerAddress, -12345) != -12345:
            return self.registerCache[registerAddress]
        else:
            value = self.modbusClient.read_holding_registers(registerAddress)
            self.registerCache[registerAddress] = value
            return value

    def getAndUpsertOpcNodeFromRegister(self, registerAddress: int):
        idx = self.registerAddressToXmlIndex.get(registerAddress, -1)
        if idx >= 0: #object data known from the xml
            try: #try to return it if it exists
                atv72object: Node = self.opcuaObjects.get_child(self.df.at[idx, 'Name'])
                value = atv72object.get_child("RegisterValue")
                value.set_value(self.readLegacyRegisterWithCaching(registerAddress))
                return atv72object
            except: #if it doesnt exist then create it and return it
                atv72object: Node = self.opcuaObjects.add_object(0, self.df.at[idx, 'Name'], self.ATV72TYPE)
                atv72object.add_variable(0, 'RegisterValue', self.readLegacyRegisterWithCaching())

                for prop in self.ATV72TYPE.get_properties():
                    p: Node = prop
                    string = str(p.get_display_name())
                    string = string.split(':')
                    string = string[string.__len__() - 1].split(')')

                    atv72object.add_property(0, string[0], str(self.df.at[idx, string[0]]))

                return atv72object
        else: #object data UNKNOWN so create one with UKNOWN field data everywhere
            atv72object: Node = self.opcuaObjects.add_object(0, "UNKNOWN_" + str(registerAddress), self.ATV72TYPE)
            atv72object.add_variable(0, 'RegisterValue', self.readLegacyRegisterWithCaching(registerAddress))

            for prop in self.ATV72TYPE.get_properties():
                p: Node = prop
                string = str(p.get_display_name())
                string = string.split(':')
                string = string[string.__len__() - 1].split(')')

                atv72object.add_property(0, string[0], "UKNOWN")

            return atv72object

    def writeToLegacyDeviceAndCache(self, registerAddress:int, value:int):
        self.modbusClient.write_single_register(registerAddress, value)
        if self.registerCache.get(registerAddress, -12345) != -12345:
            self.registerCache[registerAddress] = value
            self.getAndUpsertOpcNodeFromRegister(registerAddress)

#modbusClient = ModbusClient('localhost', 12000)
#print("Starting Edge device")
#modbusClient.open()
## parse the xls into opc ua object types
#opcuaServer = Server()
#
#opcuaObjects = opcuaServer.get_objects_node()
#noEntriesInitialized = 100
#noEntriesUpdated = 931
#opcuaServer.export_xml(opcuaObjects.get_referenced_nodes(), "opcuanodes.xml")

#try:
#    opcuaServer.start()
#
#    edgeDevice = EdgeDevice()
#    edgeDevice.initializeFromLegacy()
#    while True:
#        edgeDevice.queryLegacy()
#except Exception as e:
#    print(e)
#    opcuaServer.stop()
#    print("Stopping Edge device")
#    modbusClient.close()
