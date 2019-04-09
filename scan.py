

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
import hid

# May want to provide some sort of CLI for these settings, perhaps using data from the GUI

# response = readCommand(h, 0x02, 0x20, [0x00, 124])
# print("Read stored scan configurations: ",response)

# response = readCommand(h, 0x02, 0x22)
# print("Read number of stored scan configurations: ",response)

# response = readCommand(h, 0x02, 0x23)
# print("Read active scan configuration : ",response)


NNO_FILE_SCAN_DATA = 0x00
NNO_FILE_REF_CAL_COEFF = 0x02

class Spectrometer():

    def __init__(self, vid, pid, serial_no=None):
        self.serial_no = serial_no
        self.vid = vid
        self.pid = pid
        self.connected_flag = False
        self.h = hid.device()
        self.reconnect_device()



    def reconnect_device(self):
        try:
            logging.debug("Attempting reconnect to spectrometer")
            #TODO Test if this if statement is needed by the HID library
            if self.serial_no:
                self.h.open(self.vid, self.pid, self.serial_no)
            else:
                self.h.open(self.vid, self.pid)
            self.connected_flag = True
            self.h.set_nonblocking(0)
            self.check_hibernate_flag()
            logging.info("Successfully reconnected to spectrometer")
        except OSError as open_failed:
            self.connected_flag = False
            return False
        return True

    def write_command(self, *args):
        try:
            return writeCommand(*args)
        except ValueError as error:
            print(error)
            self.connected_flag = False
            raise error

    def read_command(self, *args):
        try:
            return readCommand(*args)
        except ValueError as error:
            print(error)
            self.connected_flag = False
            raise error

    def perform_scan(self):
        if not self.connected_flag:
            if not self.reconnect_device():
                return
        # Set the active scan configuration
        response = self.write_command(self.h, 0x02, 0x24, [0x01])
        logging.debug("Set the active scan configuration: ",response)

        # response = self.read_command(h, 0x02, 0x23)
        # print("Read active scan configuration : ",response)

        # Write the start scan command, data 0x00, since we don't want to store the scan in the SD card
        response = self.write_command(self.h, 0x02, 0x18, [0x00])
        logging.debug("Write the start scan command: ", response)

        # Read the device status
        logging.info("Scan in progress")
        device_status = self.read_command(self.h, 0x04, 0x03)

        while(device_status[0] & 0x02 == 0x02):
            time.sleep(0.1)
            device_status = self.read_command(self.h, 0x04, 0x03)
        logging.info("Scan complete")

    def get_file(self, file_to_read):
        if not self.connected_flag:
            if not self.reconnect_device():
                return
        # NNO_CMD_FILE_GET_READSIZE
        # data size in bytes
        data_size = self.read_command(self.h, 0x00, 0x2D, [file_to_read])
        logging.debug("data size: ", data_size)
        data_size.reverse()
        data_size_combined = shiftBytes(data_size)

        # Actually get the file
        # repeatedly NNO_GetFileData
        file = []
        while (len(file) < data_size_combined):
            data = self.read_command(self.h, 0x00, 0x2E)
            file.extend(data)

        # print("Recieved file length: ", len(file))
        # print("Expected file length: ", data_size_combined)

        return file


    def check_hibernate_flag(self):
        if not self.connected_flag:
            if not self.reconnect_device():
                return
        hibernate_flag_status = self.read_command(self.h, 0x03, 0x0F)
        logging.debug("Hibernate flag status: {}".format(hibernate_flag_status))
        if hibernate_flag_status[0] == 1:
            response = self.write_command(self.h, 0x03, 0x0E, [0])
            hibernate_flag_status = self.read_command(self.h, 0x03, 0x0F)
            logging.debug("Updated hibernate flag status: {}".format(hibernate_flag_status))


# can also get calibration data evm.cpp:107


# need to check that this hasn't changed, and is continually