

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
from util import shiftBytes

h = hid.device()
try:
    print("Opening the device")
    h.open(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
except IOError as ex:
    print(ex)
    print("Looks like the NIRScan Nano isn't connected")
    exit()

# enable non-blocking mode
h.set_nonblocking(0)

response = readCommand(h, 0x02, 0x20, [0x00, 124])
print("Read stored scan configurations: ",response)

response = readCommand(h, 0x02, 0x22)
print("Read number of stored scan configurations: ",response)

response = readCommand(h, 0x02, 0x23)
print("Read active scan configuration : ",response)

# Set the active scan configuration
response = writeCommand(h, 0x02, 0x24, [0x01])
print("Set the active scan configuration: ",response)

# time.sleep(1)

response = readCommand(h, 0x02, 0x23)
print("Read active scan configuration : ",response)

# Write the start scan command, data 0x00, since we don't want to store the scan in the SD card
response = writeCommand(h, 0x02, 0x18, [0x00])
print("Write the start scan command: ", response)

# time.sleep(0.5)
# Read the device status
print("Scan in progress")
device_status = readCommand(h, 0x04, 0x03)

while(device_status[0] & 0x02 == 0x02):
    time.sleep(0.1)
    device_status = readCommand(h, 0x04, 0x03)
print("Scan complete")






# NNO_CMD_FILE_GET_READSIZE
# Data byte = NNO_FILE_SCAN_DATA
# data size in bytes
data_size = readCommand(h, 0x00, 0x2D, [0x00])
print("data size: ", data_size)
data_size.reverse()
data_size_combined = shiftBytes(data_size)

# Actually get the file
# repeatedly NNO_GetFileData
file = []
# print("Expected file length: ", data_size_combined)

while(len(file) < data_size_combined):
    data = readCommand(h, 0x00, 0x2E)
    # data.reverse()
    file.extend(data)
    # print("file length: ", len(file))


print("Recieved file length: ", len(file))
print("Expected file length: ", data_size_combined)

byte_file = bytearray(file)
print(byte_file)
print(file)



# Read the calibration
# NNO_CMD_FILE_GET_READSIZE
# Data byte = NNO_FILE_SCAN_DATA
# data size in bytes
data_size = readCommand(h, 0x00, 0x2D, [0x02])
print("data size: ", data_size)
data_size.reverse()
data_size_combined = shiftBytes(data_size)

# Actually get the file
# repeatedly NNO_GetFileData
file2 = []
# print("Expected file length: ", data_size_combined)

while(len(file2) < data_size_combined):
    data = readCommand(h, 0x00, 0x2E)
    # data.reverse()
    file2.extend(data)
    # print("file length: ", len(file))


print("Recieved file length: ", len(file2))
print("Expected file length: ", data_size_combined)

byte_file2 = bytearray(file2)
print(byte_file2)
print(file2)

combined_bytes = file.copy()

combined_bytes.extend(file2)

byte_file_combined = bytearray(combined_bytes)








newFile = open("binary.dat", "wb")
newFile.write(byte_file_combined)

from test_dll import *

results = scanResults()
print(results)

res_pointer = ctypes.pointer(results)
print(res_pointer)

buffer = ctypes.create_string_buffer(len(byte_file), byte_file)
buffer_pointer = ctypes.byref(buffer)

size_number = ctypes.c_size_t(len(byte_file))
print(size_number)
dlp_nano_lib.dlpspec_scan_interpret(buffer_pointer, size_number, res_pointer)



# can also get calibration data evm.cpp:107


# need to check that this hasn't changed, and is continually