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
    excelData = pd.read_excel('data/ATV71_communication_parameters_EN_V5.7_IE67.xls', 1)
    noKnownRegisters = 5
    idx = 0
    registersToModify = list()
    df = pd.DataFrame(excelData)
    for i in range(0, 931):
        registerString = df.at[i, 'Logic\naddress']
        if registerString != '-':
            numbers = regex.findall(r'\d+', registerString)
            registerAddress = (int)(numbers[numbers.__len__() - 1])

            if idx < 5:
                registersToModify.append(registerAddress)
                idx = idx + 1
            
            server.data_bank.set_holding_registers(registerAddress, [-1])
    print("Legacy device: Filling registers with default values ended")
    random.seed(0)
    noRandomRegisters = 5
    for i in range(0, noRandomRegisters):
        registersToModify.append((int)(random.random() * 32000))

    idx = 0
    while True:
        time.sleep(1)
        if idx >= 10:
            idx = 0
        randomRegister = registersToModify[idx]
        idx = idx + 1
        randomValue = (int)(random.random() * 32000)
        oldValue = server.data_bank.get_holding_registers(randomRegister)
        server.data_bank.set_holding_registers(randomRegister, [randomValue])
        print("register " + str(randomRegister) + " changed its value from " + str(oldValue) + " to " + str(randomValue))
        continue
except BaseException as e:
    print(e)
    print("Legacy device stopping...")
    server.stop()
    print("Legacy device stopped")