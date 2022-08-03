from pyModbusTCP.server import ModbusServer, DataBank
import pandas as pd
import re as regex
import time
import random
server = ModbusServer('localhost', 12000, True)

#setting up default data
try:
    registers = []
    print("Starting Legacy device...")
    server.start()
    print("Legacy device started. Filling the registries with default data")
    excelData = pd.read_excel('ATV71_communication_parameters_EN_V5.7_IE67.xls', 1)
    df = pd.DataFrame(excelData)
    for i in range(0, 931):
        registerString = df.at[i, 'Logic\naddress']
        if registerString != '-':
            numbers = regex.findall(r'\d+', registerString)
            registerAddress = (int)(numbers[numbers.__len__() - 1])
            registers.append(registerAddress)
            registerValueType = (str)(df.at[i, 'Type'])
            defaultSetting = (str)(df.at[i, 'Factory setting'])
            server.data_bank.set_holding_registers(registerAddress, [-1])
    print("Filling ended")
    while True:
        time.sleep(5)
        randomRegisterIndex = (int)(random.random() * registers.__len__() - 1)
        randomRegister = registers[randomRegisterIndex]
        randomValue = (int)(random.random() * 32000)
        server.data_bank.set_holding_registers(randomRegister, [randomValue])
        print("register " + str(randomRegister) + " changed to " + str(randomValue))
        continue
except BaseException as e:
    print(e)
    print("Legacy device stopping...")
    server.stop()
    print("Legacy device stopped")