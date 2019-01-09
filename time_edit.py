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

# Read the current device time
device_time_list = readCommand(h, 0x03, 0x0C)
print(device_time_list)

# Add 5 minutes to the time
device_time_list[-2] += 5

# Write the updated device time
response = writeCommand(h, 0x03, 0x09, device_time_list)

# Print the response
print(response)

new_device_time_list = readCommand(h, 0x03, 0x0C)

# Print the changed device time
print(new_device_time_list)

# Close the device
h.close()