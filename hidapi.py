from __future__ import print_function

import hid
import time

# enumerate USB devices

# for d in hid.enumerate():
#     keys = list(d.keys())
#     keys.sort()
#     for key in keys:
#         print("%s : %s" % (key, d[key]))
#     print()

# try opening a device, then perform write and read

try:
    print("Opening the device")

    h = hid.device()
    h.open(0x0451, 0x4200) # NIRScan Nano VendorID/ProductID

    # print("Manufacturer: %s" % h.get_manufacturer_string())
    # print("Product: %s" % h.get_product_string())
    # print("Serial No: %s" % h.get_serial_number_string())

    # enable non-blocking mode
    h.set_nonblocking(1)

    # write some data to the device
    print("Write the data")

    # h.write([0x00, 0xC0, 0x00, 0x02, 0x00, 0x33, 0x02])
    h.write([0x00, 0xC0, 0x00, 0x02, 0x00, 0x0C, 0x03])
    # ^ returns: 192, 0, 8, 0, 54, 52, 54, 48, 48, 57, 49,

    # h.write([0x02, 0x33, 0x00, 0x02, 0x00, 0xC0, 0x00])


    # wait
    time.sleep(1)

    # read back the answer
    print("Read the data")
    while True:
        d = h.read(64)
        if d:
            print(d)
            print("Command Requested By Host: ", "".join('{:02X}'.format(x) for x in d[0:1]))
            print("Response Length: {} bytes".format(d[2]))
            print(d[4:(d[2]+4)])
        else:
            break

    print("Closing the device")
    h.close()

    [15, 3, 31, 2, 7, 9, 55]

except IOError as ex:
    print(ex)
    print("You probably don't have the hard coded device. Update the hid.device line")
    print("in this script with one from the enumeration list output above and try again.")

print("Done")