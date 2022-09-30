# OPC-UA-interface

To install all the required packages, on UNIX-based OS please run
```bash
bash install.sh
```

This is an Industry 4.0 edge mockup. To emulate the communication among devices, open a terminal and start a legacy device first
```bash
python3 legacy/legacy_device.py
```

On a new terminal, launch the software
```bash
python3 main.py
```
To start the serial communication, please enable the listening thrugh the UI, as shown in the following GIF.

<p align="center">
  <img src="/media/demo.gif">
  </p>
