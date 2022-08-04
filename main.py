import tkinter as tk
import tkinter.font as font

import psutil
import platform
import datetime
import time
from PIL import ImageTk, Image
from server.edge_device import *
from opcua.common.xmlexporter import XmlExporter


NCOLUMNS = 9
NROWS    = 30
SIDEMENU_COLUMNS = 2
DEVICE_COLUMNS   = 2
PAD_X = 20

SIDEMENU_COLOR         = '#cce0ff'
DEVICE_FAMILY_COLOR   = '#e6e6e6'
DEVICE_LIST_COLOR   = '#f2f2f2'
DETAILED_SECTION_COLOR = '#ffffff'
BOTTOM_MENU_COLOR      = '#0066ff'
SELECTED_FAMILY = None
SELECTED_DEVICE = None

FETCHED_REGISTRIES = 10
SHOW_DATA = None

dev = {'len':13,
       'MODBUS-RTU':['TC0451','TB3421','PO0187','ZJ3253'],
       'MODBUS-TCP':['TP-1312','RM-3112','ZZ53412','CW5823',],
       'FIELDBUS'  :['D4512','AZ24785','SD2342','FH5323','AF7593']
}

def showOPCUA(index):
    global SHOW_DATA
    SHOW_DATA = index

def serverLoop():
    try:
        edgeDevice.queryLegacyAndUpdateCache()

        dummy = 0
        #OPC-UA object
        for i in edgeDevice.registersToWatch:
            #get the modbus value

            mytable[dummy][0]['text'] = i
            mytable[dummy][1]['text'] = edgeDevice.readLegacyRegisterWithCaching(i)

            dummy += 1
            # get the OPC-UA values
            obj = edgeDevice.getAndUpsertOpcNodeFromRegister(i)
            opcuaServer.export_xml(obj.get_children(), "cache/opcuanodes-%i.xml" % (i))
            if SHOW_DATA == dummy:
                myOPCdata = open("cache/opcuanodes-%i.xml" % (i),'r')
                OPCdata.delete('1.0',tk.END)
                OPCdata.insert(tk.END,myOPCdata.read())
                myOPCdata.close()


    except Exception as e:
        print(e)
        opcuaServer.stop()
        print("Stopping Edge device")
        modbusClient.close()
    
    root.after(500,serverLoop)


def startService():
    global edgeDevice, modbusClient, opcuaServer
    lab02['text'] = 'Starting...'
    lab02['fg']  = 'orange'
    try:
        modbusClient = ModbusClient('localhost', 12000)
        print("Starting Edge device")
        modbusClient.open()
        # parse the xls into opc ua object types
        opcuaServer = Server()

        opcuaObjects = opcuaServer.get_objects_node()
        
        noEntriesInitialized = 931
        noEntriesUpdated = 931

        edgeDevice = EdgeDevice(opcuaServer,modbusClient,opcuaObjects,noEntriesInitialized)
        edgeDevice.initializeFromLegacy()

        lab02['text'] = 'Active'
        lab02['fg']  = 'green'

    except Exception as e:
        print(e)
        opcuaServer.stop()
        print("startService : Stopping Edge device")
        modbusClient.close()
    serverLoop()


def onDeviceFamilyClick(name):
    global SELECTED_FAMILY
    frame03['bg'] = DEVICE_LIST_COLOR
    lab08['bg']   = DEVICE_LIST_COLOR
    SELECTED_FAMILY = name
    for i in range(len(dev[name])):
        if i==0:
            tk.Button(root,text=dev[name][i],activebackground=DEVICE_LIST_COLOR,
                        padx=PAD_X,bd=0,command=lambda val=dev[name][i]: onDeviceClick(val),
                            bg = DEVICE_LIST_COLOR,highlightthickness=0,anchor='w'
                        ).grid(column=SIDEMENU_COLUMNS+DEVICE_COLUMNS,row=i+1,sticky='NWSE',columnspan=DEVICE_COLUMNS)

            tk.Label(root, image = statusOnline,bg=DEVICE_LIST_COLOR,width=10, height=10, activebackground=DETAILED_SECTION_COLOR
            ).grid(row=i+1,column=SIDEMENU_COLUMNS+DEVICE_COLUMNS+1,columnspan=1,sticky='NSE',padx=PAD_X)
        else:
            tk.Button(root,text=dev[name][i],activebackground=DEVICE_LIST_COLOR,
                        padx=PAD_X,bd=0,command=lambda val=dev[name][i]: onDeviceClick(val),
                            bg = DEVICE_LIST_COLOR,highlightthickness=0,anchor='w'
                        ).grid(column=SIDEMENU_COLUMNS+DEVICE_COLUMNS,row=i+1,sticky='NWSE',columnspan=DEVICE_COLUMNS)

            tk.Label(root, image = statusOffline,bg=DEVICE_LIST_COLOR,width=10, height=10, activebackground=DETAILED_SECTION_COLOR
            ).grid(row=i+1,column=SIDEMENU_COLUMNS+DEVICE_COLUMNS+1,columnspan=1,sticky='NSE',padx=PAD_X)


def onDeviceClick(name):
    global SELECTED_DEVICE
    lab_dev['text'] = name
    SELECTED_DEVICE = name

    tk.Label(root,text='Registry',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black').grid(
    row=2,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NWSE')

    tk.Label(root,text='Native value',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black').grid(
    row=2,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+1,sticky='NWSE')

    for i in range(FETCHED_REGISTRIES):
        #get the modbus value

        mytable[i][0].grid(row=i+3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS  ,sticky='NWSE')
        mytable[i][1].grid(row=i+3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+1,sticky='NWSE')
        mytable[i][2].grid(row=i+3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+2,sticky='NWSE')
    OPCdata.grid(row=i+4,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS  ,sticky='NWSE',columnspan=3,rowspan=NROWS-(i+4))
    update(name)


def coolBottomBar():
    labRAM['text'] = 'Ram usage: ' + str(psutil.virtual_memory().percent)
    cpu = psutil.cpu_percent()
    if (cpu >= 10):
        labCPU['text'] = 'CPU usage: ' + str(cpu)
    else:
        labCPU['text'] = 'CPU usage:  ' + str(cpu)
    if platform.system() == 'Linux':
        labTEMP['text'] = 'CPU temperature: ' + str(psutil.sensors_temperatures()['coretemp'][1][1])
    
    uptime['text']  = '10d ' + datetime.datetime.now().strftime('%Hh %Mmin %Ssec')

    root.after(500,coolBottomBar)


def update(device=0):
    if device:
        '''frame05.grid_forget()
        lab09  .grid_forget()
        cbID   .grid_forget()
        cbTemp .grid_forget()
        cbClock.grid_forget()

        data00['text'] = 'Connection type: '
        data01['text'] = 'Data received:  '
        data02['text'] = 'Data converted: '
        data03['text'] = 'Incoming data: '
        data04['text'] = 'OPC-UA conversion: '

        data00v['text'] = SELECTED_FAMILY
        data01v['text'] = '- '
        data02v['text'] = '-  '
        data03v['text'] = '- '
        data04v['text'] = '- '
        '''
        
        '''tk.Button(root,text='Configure parameters',activebackground=SIDEMENU_COLOR,
                    padx=0,pady=0,bd=0,command=onConfigureClick,
                         bg = DEVICE_LIST_COLOR,highlightthickness=0
                    ).grid(column=NCOLUMNS-1,row=NROWS-2,sticky='NWSE',columnspan=1,padx=PAD_X,pady=PAD_X)
        '''
        root.after(10,update)


root = tk.Tk()
root.geometry("1440x800")
root.minsize(1200,700)
root.title('Rosetta 4.0 - Premium')

company_font = font.Font(size=30, weight='bold')
justBold     = font.Font(weight='bold')
dev_font     = font.Font(weight='bold', size=20)

for i in range(NCOLUMNS):
    root.grid_columnconfigure(i,weight=1)

for i in range(NROWS):
    root.grid_rowconfigure(i,weight=1)


statusOnline = ImageTk.PhotoImage(Image.open("assets/green_dot.png").resize((10, 10)))
statusOffline = ImageTk.PhotoImage(Image.open("assets/red_dot.png").resize((10, 10)))

#==========SIDEMENU==========
frame01 = tk.Frame(root, bg=SIDEMENU_COLOR)
frame01.grid(column=0,row=0,columnspan=SIDEMENU_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame01.grid_propagate(0)

lab00 = tk.Label(root,text='Rosetta 4.0',bg=SIDEMENU_COLOR)
lab00['font'] = company_font
lab00.grid(row=0,column=0,sticky='NWSE',rowspan=2,columnspan=SIDEMENU_COLUMNS)


lab01 = tk.Label(root,text='Status: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=2,column=0,sticky='NW',padx=PAD_X)
lab02 = tk.Label(root,text='Stopped',fg='red',bg=SIDEMENU_COLOR,font=justBold)
lab02.grid(row=2,column=1,sticky='NW')

lab03 = tk.Label(root,text='Connected devices: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=3,column=0,sticky='NW',padx=PAD_X)
lab04 = tk.Label(root,text=str(dev['len']),bg=SIDEMENU_COLOR).grid(row=3,column=1,sticky='NW')

lab05 = tk.Label(root,text='Warnings: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=4,column=0,sticky='NW',padx=PAD_X)
lab06 = tk.Label(root,text='0 ',bg=SIDEMENU_COLOR).grid(row=4,column=1,sticky='NW')

tk.Label(root,text='Uptime: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=5,column=0,sticky='NW',padx=PAD_X)
uptime = tk.Label(root,text='0 ',bg=SIDEMENU_COLOR)
uptime.grid(row=5,column=1,sticky='NW')

tk.Button(root,text='Start communication',activebackground=SIDEMENU_COLOR,
                    padx=0,pady=0,bd=0,command=lambda : startService(),
                         bg = DEVICE_LIST_COLOR,highlightthickness=0
                    ).grid(column=0,row=NROWS-2,sticky='NWSE',columnspan=1,padx=PAD_X,pady=PAD_X)



#==========DEVICE FAMILY LIST==========
frame02 = tk.Frame(root, bg=DEVICE_FAMILY_COLOR)
frame02.grid(column=SIDEMENU_COLUMNS,row=0,columnspan=DEVICE_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame02.grid_propagate(0)

lab07 = tk.Label(root,text='Detected protocols ',bg=DEVICE_FAMILY_COLOR,font=justBold).grid(row=0,column=SIDEMENU_COLUMNS,columnspan=DEVICE_COLUMNS,sticky='NWS',padx=PAD_X)

# Fill the interface with the available connected devices


for i in range(1,len(dev.keys())):
    if i==1:
        tk.Button(root,text=list(dev.keys())[i],activebackground=DEVICE_LIST_COLOR,
                            padx=PAD_X,bd=0,command=lambda val=list(dev.keys())[i]: onDeviceFamilyClick(val),
                            bg = DEVICE_FAMILY_COLOR,highlightthickness=0, anchor='w'
        ).grid(column=SIDEMENU_COLUMNS,row=i,sticky='NWSE',columnspan=DEVICE_COLUMNS)
    else:
        tk.Label(root,text=list(dev.keys())[i],activebackground=DEVICE_FAMILY_COLOR,
                            padx=PAD_X,bd=0,fg='#737373',
                            bg = DEVICE_FAMILY_COLOR,highlightthickness=0, anchor='w'
        ).grid(column=SIDEMENU_COLUMNS,row=i,sticky='NWSE',columnspan=DEVICE_COLUMNS)


#==========DEVICE LIST==========
frame03 = tk.Frame(root, bg=DETAILED_SECTION_COLOR)
frame03.grid(column=SIDEMENU_COLUMNS+DEVICE_COLUMNS,row=0,columnspan=DEVICE_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame03.grid_propagate(0)

lab08 = tk.Label(root,text='Devices ',bg=DETAILED_SECTION_COLOR,font=justBold)
lab08.grid(row=0,column=SIDEMENU_COLUMNS+DEVICE_COLUMNS,columnspan=DEVICE_COLUMNS,sticky='NWS',padx=PAD_X)


#==========DETAILED CONTENT==========
frame04 = tk.Frame(root, bg=DETAILED_SECTION_COLOR)
frame04.grid(column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,row=0,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame04.grid_propagate(0)

lab_dev = tk.Label(text='',font=dev_font,bg = DETAILED_SECTION_COLOR)
lab_dev.grid(row=0,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS, columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2,sticky='NWSE')

reg00  = tk.Label(root,text='Registry',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black')
reg00v = tk.Label(root,text='Native value',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black')

mytable = list()
for i in range(FETCHED_REGISTRIES):
    mytable.append([
            tk.Label(root,text='-',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black'),
            tk.Label(root,text='-',bg=DETAILED_SECTION_COLOR,font=justBold,highlightthickness=1,highlightbackground='black'),
            tk.Button(root,text='See OPC-UA data',activebackground=SIDEMENU_COLOR,padx=0,pady=0,bd=0,command=lambda var=i:showOPCUA(var),bg = DEVICE_LIST_COLOR,highlightthickness=0)
    ])

OPCdata = tk.Text(root,bg='black',fg=DETAILED_SECTION_COLOR)


#==========BOTTOM MENU==========
frame06 = tk.Frame(root, bg=BOTTOM_MENU_COLOR)
frame06.grid(column=0,row=NROWS-1,columnspan=NCOLUMNS,sticky='NWSE')
frame06.grid_propagate(0)

labRAM = tk.Label(root,text='Ram usage: -',bg=BOTTOM_MENU_COLOR,fg='white')
labRAM.grid(row=NROWS-1,column=NCOLUMNS-1,columnspan=1,sticky='NWS')

labCPU = tk.Label(root,text='CPU usage: -',bg=BOTTOM_MENU_COLOR,fg='white') 
labCPU.grid(row=NROWS-1,column=NCOLUMNS-2,columnspan=1,sticky='NWS')

labTEMP = tk.Label(root,text='CPU usage: -',bg=BOTTOM_MENU_COLOR,fg='white')
labTEMP.grid(row=NROWS-1,column=NCOLUMNS-3,columnspan=1,sticky='NWS')

tk.Label(root,text='Sotware version: 1.0.4 ', bg=BOTTOM_MENU_COLOR,fg='white').grid(row=NROWS-1,column=0,sticky='NWS',padx=PAD_X,columnspan=1)
tk.Label(root,text='Serial: SC-0123842S ', bg=BOTTOM_MENU_COLOR,fg='white').grid(row=NROWS-1,column=1,sticky='NWS',padx=PAD_X,columnspan=1)

update()
coolBottomBar()

root.mainloop()