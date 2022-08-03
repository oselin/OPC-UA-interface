import tkinter as tk
import tkinter.font as font
import psutil
import platform
import datetime
import time
from PIL import ImageTk, Image
from server.edge_device import *

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

ID    = 0
TEMP  = 0
CLOCK = 0
STARTED = 0

dev = {'len':13,
       'MODBUS-RTU':['TC0451','TB3421','PO0187','ZJ3253'],
       'MODBUS-TCP':['TP-1312','RM-3112','ZZ53412','CW5823',],
       'FIELDBUS'  :['D4512','AZ24785','SD2342','FH5323','AF7593']
}

def serverLoop():
    try:
        edgeDevice.queryLegacyAndUpdateCache()

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


def onConfigureClick():
    frame05.grid(column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,row=2,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=NROWS-1,sticky='NWSE')
    frame05.grid_propagate(0)
    #lab_dev.grid(row=0,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS, columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2,sticky='NWSE')

    lab09  .grid(row=2,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X,columnspan=3)
    cbID   .grid(row=3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NWS',padx=PAD_X)
    cbTemp .grid(row=4,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NWS',padx=PAD_X)
    cbClock.grid(row=5,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NWS',padx=PAD_X)

    tk.Button(root,text='Save and close',activebackground=SIDEMENU_COLOR,
                    padx=0,pady=0,bd=0,command=lambda: update(SELECTED_DEVICE),
                         bg = DEVICE_LIST_COLOR,highlightthickness=0
                    ).grid(column=NCOLUMNS-1,row=NROWS-2,sticky='NWSE',columnspan=1,padx=PAD_X,pady=PAD_X)


def onDeviceFamilyClick(name):
    global SELECTED_FAMILY
    frame03['bg'] = DEVICE_LIST_COLOR
    lab08['bg']   = DEVICE_LIST_COLOR
    SELECTED_FAMILY = name
    for i in range(len(dev[name])):
        tk.Button(root,text=dev[name][i],activebackground=DETAILED_SECTION_COLOR,
                    padx=PAD_X,bd=0,command=lambda val=dev[name][i]: onDeviceClick(val),
                         bg = DEVICE_LIST_COLOR,highlightthickness=0,anchor='w'
                    ).grid(column=SIDEMENU_COLUMNS+DEVICE_COLUMNS,row=i+1,sticky='NWSE',columnspan=DEVICE_COLUMNS)

        tk.Label(root, image = statusOnline,bg=DEVICE_LIST_COLOR,width=10, height=10, activebackground=DETAILED_SECTION_COLOR
        ).grid(row=i+1,column=SIDEMENU_COLUMNS+DEVICE_COLUMNS+1,columnspan=1,sticky='NSE',padx=PAD_X)


def onDeviceClick(name):
    global SELECTED_DEVICE
    lab_dev['text'] = name
    SELECTED_DEVICE = name
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
        frame05.grid_forget()
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
        
        tk.Button(root,text='Configure parameters',activebackground=SIDEMENU_COLOR,
                    padx=0,pady=0,bd=0,command=onConfigureClick,
                         bg = DEVICE_LIST_COLOR,highlightthickness=0
                    ).grid(column=NCOLUMNS-1,row=NROWS-2,sticky='NWSE',columnspan=1,padx=PAD_X,pady=PAD_X)

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
    button_i = tk.Button(root,text=list(dev.keys())[i],activebackground=DEVICE_LIST_COLOR,
                         padx=PAD_X,bd=0,command=lambda val=list(dev.keys())[i]: onDeviceFamilyClick(val),
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

data00  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data00.grid(row=2,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X)
data00v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data00v.grid(row=2,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+1,sticky='NW',padx=PAD_X)

data01  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data01.grid(row=3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X)
data01v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data01v.grid(row=3,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+1,sticky='NW',padx=PAD_X)
data02  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data02.grid(row=4,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X) 
data02v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data02v.grid(row=4,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS+1,sticky='NW',padx=PAD_X)

data03  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data03.grid(row=5,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X)
data03v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data03v.grid(row=6,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2)
data04  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data04.grid(row=8,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X)
data04v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data04v.grid(row=9,column=SIDEMENU_COLUMNS+2*DEVICE_COLUMNS,sticky='NW',padx=PAD_X,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2)

#=========SETTINGS PAGE=========
frame05 = tk.Frame(root, bg=DETAILED_SECTION_COLOR)

lab09 = tk.Label(root,text='Settings and custom queries ',bg=DETAILED_SECTION_COLOR,font=justBold)

cbID = tk.Checkbutton(root, text='ID',variable=ID, onvalue=1, offvalue=0,bg=DETAILED_SECTION_COLOR,
                    highlightthickness=0,activebackground=DETAILED_SECTION_COLOR)

cbTemp = tk.Checkbutton(root, text='Temperature',variable=TEMP, onvalue=1, offvalue=0,bg=DETAILED_SECTION_COLOR,
                    highlightthickness=0,activebackground=DETAILED_SECTION_COLOR)

cbClock = tk.Checkbutton(root, text='Clock',variable=CLOCK, onvalue=1, offvalue=0,bg=DETAILED_SECTION_COLOR,
                    highlightthickness=0,activebackground=DETAILED_SECTION_COLOR)


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