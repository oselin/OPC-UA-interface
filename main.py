from ctypes.wintypes import SHORT
import tkinter as tk
import tkinter.font as font
from matplotlib.pyplot import show
import psutil
 
NCOLUMNS = 7
NROWS    = 30
SIDEMENU_COLUMNS = 2
PAD_X = 20

SIDEMENU_COLOR         = '#cce0ff'
DEVICE_SECTION_COLOR   = '#eeeeee'
DETAILED_SECTION_COLOR = '#ffffff'
BOTTOM_MENU_COLOR      = '#0066ff'
SELECTED_DEVICE = None

dev = ['TC0451','TB3421','PO0187','ZJ3253','TP-1312','RM-3112','ZZ53412','CW5823','D4512','AZ24785','SD2342','FH5323','AF7593']

def deviceClick(name):
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
    root.after(500,coolBottomBar)

def update(device=0):
    if device:
        data00['text'] = 'Connection type: '
        data01['text'] = 'Data received:  '
        data02['text'] = 'Data converted: '
        data03['text'] = 'Incoming data: '
        data04['text'] = 'OPC-UA conversion: '

        data00v['text'] = 'MODBUS'
        data01v['text'] = '- '
        data02v['text'] = '-  '
        data03v['text'] = '- '
        data04v['text'] = '- '
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



#==========SIDEMENU==========
frame01 = tk.Frame(root, bg=SIDEMENU_COLOR)
frame01.grid(column=0,row=0,columnspan=SIDEMENU_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame01.grid_propagate(0)

lab00 = tk.Label(root,text='Rosetta 4.0',bg=SIDEMENU_COLOR)
lab00['font'] = company_font
lab00.grid(row=0,column=0,sticky='NWSE',rowspan=2,columnspan=SIDEMENU_COLUMNS)


lab01 = tk.Label(root,text='Status: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=2,column=0,sticky='NW',padx=PAD_X)
lab02 = tk.Label(root,text='Active',fg='green',bg=SIDEMENU_COLOR,font=justBold).grid(row=2,column=1,sticky='NW')

lab03 = tk.Label(root,text='Connected devices: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=3,column=0,sticky='NW',padx=PAD_X)
lab04 = tk.Label(root,text=str(len(dev)),bg=SIDEMENU_COLOR).grid(row=3,column=1,sticky='NW')

lab05 = tk.Label(root,text='Warnings: ',bg=SIDEMENU_COLOR,font=justBold).grid(row=4,column=0,sticky='NW',padx=PAD_X)
lab06 = tk.Label(root,text='0 ',bg=SIDEMENU_COLOR).grid(row=4,column=1,sticky='NW')


#==========DEVICE LIST==========
frame02 = tk.Frame(root, bg=DEVICE_SECTION_COLOR)
frame02.grid(column=2,row=0,columnspan=SIDEMENU_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame02.grid_propagate(0)

lab07 = tk.Label(root,text='Device list: ',bg=DEVICE_SECTION_COLOR,font=justBold).grid(row=0,column=2,columnspan=2,sticky='NWS',padx=PAD_X)

# Fill the interface with the available connected devices



for i in range(len(dev)):
    button_i = tk.Button(root,text=dev[i],activebackground=DETAILED_SECTION_COLOR,
                         padx=0,pady=0,bd=0,command=lambda val=dev[i]: deviceClick(val),
                         bg = DEVICE_SECTION_COLOR,border=0
    ).grid(column=2,row=i+1,sticky='NWSE',columnspan=2)

#==========DETAILED CONTENT==========
frame03 = tk.Frame(root, bg=DETAILED_SECTION_COLOR)
frame03.grid(column=4,row=0,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=NROWS,sticky='NWSE')
frame03.grid_propagate(0)

lab_dev = tk.Label(text='',font=dev_font,bg = DETAILED_SECTION_COLOR)
lab_dev.grid(row=0,column=4, columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2,sticky='NWSE')

data00  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data00.grid(row=2,column=4,sticky='NW',padx=PAD_X)
data00v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data00v.grid(row=2,column=5,sticky='NW',padx=PAD_X)

data01  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data01.grid(row=3,column=4,sticky='NW',padx=PAD_X)
data01v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data01v.grid(row=3,column=5,sticky='NW',padx=PAD_X)
data02  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data02.grid(row=4,column=4,sticky='NW',padx=PAD_X) 
data02v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data02v.grid(row=4,column=5,sticky='NW',padx=PAD_X)

data03  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data03.grid(row=5,column=4,sticky='NW',padx=PAD_X)
data03v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data03v.grid(row=6,column=4,sticky='NW',padx=PAD_X,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2)
data04  = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data04.grid(row=8,column=4,sticky='NW',padx=PAD_X)
data04v = tk.Label(root,text='',bg=DETAILED_SECTION_COLOR,font=justBold)
data04v.grid(row=9,column=4,sticky='NW',padx=PAD_X,columnspan=NCOLUMNS - 2*SIDEMENU_COLUMNS,rowspan=2)

#==========BOTTOM MENU==========
frame04 = tk.Frame(root, bg=BOTTOM_MENU_COLOR)
frame04.grid(column=0,row=NROWS-1,columnspan=NCOLUMNS,sticky='NWSE')
frame04.grid_propagate(0)

labRAM = tk.Label(root,text='Ram usage: -',bg=BOTTOM_MENU_COLOR,fg='white')
labRAM.grid(row=NROWS-1,column=NCOLUMNS-1,columnspan=1,sticky='NWS')

labCPU = tk.Label(root,text='CPU usage: -',bg=BOTTOM_MENU_COLOR,fg='white')
labCPU.grid(row=NROWS-1,column=NCOLUMNS-2,columnspan=1,sticky='NWS')

tk.Label(root,text='Sotware version: 1.0.4 ', bg=BOTTOM_MENU_COLOR,fg='white').grid(row=NROWS-1,column=0,sticky='NWS',padx=PAD_X,columnspan=1)
tk.Label(root,text='Serial: SC-0123842S ', bg=BOTTOM_MENU_COLOR,fg='white').grid(row=NROWS-1,column=1,sticky='NWS',padx=PAD_X,columnspan=1)

update()
coolBottomBar()

root.mainloop()