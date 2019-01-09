from __future__ import print_function

import hid
import time

h = hid.device()
try:
    print("Opening the device")
    h.open(0x0451, 0x4200) # NIRScan Nano VendorID/ProductID
except IOError as ex:
    print(ex)
    print("Looks like the NIRScan Nano isn't connected")
    exit()

# enable non-blocking mode
h.set_nonblocking(1)

# Start the read transaction
h.write([
    0x00, # ID Byte, set to 0
    0xC0, # Flags Byte 1100 0000  Read, wants a reply
    0x00, # Sequence Byte
    0x02, # Length of data (LSB)
    0x00, # Length of data (MSB)
    0x0C, # Command Byte
    0x03  # Group Byte
])

# wait
time.sleep(0.05)

# read back the answer
# TODO:  dynamically read the correct number of bytes
d = []
while True:
    d2 = h.read(64)
    if d2:
        d.extend(d2)
    else:
        break

if d:
    # print(d)
    print("Command Requested By Host: ", "".join('{:02X}'.format(x) for x in d[0:1]))
    print("Response Length: {} bytes".format(d[2]))
    print(d[4:(d[2]+4)])

print("Closing the device")
h.close()

[15, 3, 31, 2, 7, 9, 55]



print("Done")