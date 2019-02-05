

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

import time
from usb import readCommand, writeCommand
from util import shiftBytes
import logging
import asyncio

# May want to provide some sort of CLI for these settings, perhaps using data from the GUI

# response = readCommand(h, 0x02, 0x20, [0x00, 124])
# print("Read stored scan configurations: ",response)

# response = readCommand(h, 0x02, 0x22)
# print("Read number of stored scan configurations: ",response)

# response = readCommand(h, 0x02, 0x23)
# print("Read active scan configuration : ",response)


NNO_FILE_SCAN_DATA = 0x00
NNO_FILE_REF_CAL_COEFF = 0x02

def get_file(h, file_to_read):
    # NNO_CMD_FILE_GET_READSIZE
    # data size in bytes
    data_size = readCommand(h, 0x00, 0x2D, [file_to_read])
    logging.debug("data size: ", data_size)
    data_size.reverse()
    data_size_combined = shiftBytes(data_size)

    # Actually get the file
    # repeatedly NNO_GetFileData
    file = []
    while (len(file) < data_size_combined):
        data = readCommand(h, 0x00, 0x2E)
        file.extend(data)

    # print("Recieved file length: ", len(file))
    # print("Expected file length: ", data_size_combined)

    return file

def perform_scan(h):
    # Set the active scan configuration
    response = writeCommand(h, 0x02, 0x24, [0x01])
    logging.debug("Set the active scan configuration: ",response)

    # response = readCommand(h, 0x02, 0x23)
    # print("Read active scan configuration : ",response)

    # Write the start scan command, data 0x00, since we don't want to store the scan in the SD card
    response = writeCommand(h, 0x02, 0x18, [0x00])
    logging.debug("Write the start scan command: ", response)

    # Read the device status
    logging.info("Scan in progress")
    device_status = readCommand(h, 0x04, 0x03)

    while(device_status[0] & 0x02 == 0x02):
        time.sleep(0.1)
        device_status = readCommand(h, 0x04, 0x03)
    logging.info("Scan complete")


# can also get calibration data evm.cpp:107


# need to check that this hasn't changed, and is continually