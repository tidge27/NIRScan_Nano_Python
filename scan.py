

 # This is a handler function for pushButton_scan on Scan Tab clicked() event
 # This function does the following tasks
 # Checks for USB connection
 # gets the selected Scan Configuration parameters - estimates the scan time and displays
 # does the scan by calling the corresponding API functions
 # saves the scan results in .csv and .bat files in user settings directory
 # displays the spectrum - plots the scan data on the GUI

 # Looking at lines 331 scantab.cpp



 # get a file ready to write to

 # PerformScanReadData(NNO_DONT_STORE_SCAN_IN_SD, ui->spinBox_numRepeat->value(), pData, &fileSize);


 # 1517 mainwindow.cpp

 #  API.cpp 809

#  dlpu030g.pdf pg. 50

# This details how to perform a scan


import hid
import time
from usb import readCommand, writeCommand

h = hid.device()
try:
    print("Opening the device")
    h.open(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
except IOError as ex:
    print(ex)
    print("Looks like the NIRScan Nano isn't connected")
    exit()

# enable non-blocking mode
h.set_nonblocking(1)


# Write the start scan command, data 0x00, since we don't want to store the scan in the SD card
response = writeCommand(h, 0x02, 0x18, [0x00])


# Read the device status
device_status = readCommand(h, 0x04, 0x03)
print(device_status)

while(device_status == [0x00, 0x00, 0x00, 0x02]):
    time.sleep(0.1)
    device_status = readCommand(h, 0x04, 0x03)

# NNO_CMD_FILE_GET_READSIZE
# Data = NNO_FILE_SCAN_DATA
data_size = readCommand(h, 0x00, 0x2D, [0x00])



# need to check that this hasn't changed, and is continually