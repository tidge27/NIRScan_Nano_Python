from scan import get_file, perform_scan, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
import hid
from spectrum_library import scan_interpret
import json
import matplotlib.pyplot as plt
from os import walk
import asyncio



# Try to open the device, otherwise read in file data
h = hid.device()
device_open = True
try:
    print("Opening the device")
    h.open(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
except IOError as ex:
    print(ex)
    print("Looks like the NIRScan Nano isn't connected")
    print("Opening the .dat file instead")
    device_open = False


if device_open:
    # disable non-blocking mode, makes life easier, sacrifices speed
    h.set_nonblocking(0)

    # Do scan
    perform_scan(h)

    # Get scan data
    scan_data = get_file(h, NNO_FILE_SCAN_DATA)
    # Get calibration data
    reference_data = get_file(h, NNO_FILE_REF_CAL_COEFF)

    # combine the data and save the dat file (readable by the GUI program provided by TI)
    byte_file_combined = bytearray(scan_data + reference_data)

    existing = ["-1.dat"]
    for (dirpath, dirnames, filenames) in walk("data"):
        existing.extend(filenames)
        break
    existing = [int(file[: -4]) for file in existing]
    existing.sort()
    file_index = existing[-1] + 1
    file_save_name = str(file_index).zfill(4)

    newFile = open("data/{}.dat".format(file_save_name), "wb")
    newFile.write(byte_file_combined)
else:
    # Open the binary
    file_save_name = "0003"
    with open("data/{}.dat".format(file_save_name), "rb") as binaryfile:
        myArr = bytearray(binaryfile.read())
    # send the first half through to the interpret function
    scan_data = myArr[:int(len(myArr)/2)]

# Interpret data
data = scan_interpret(scan_data)
data_dict = json.loads(data)

print(data)
print("Enter JSON save prefix")
jsonFile = open("json/{}_{}.JSON".format(input(), file_save_name), "w")
jsonFile.write(data)

plt.plot(
    data_dict["wavelength"][0:data_dict["length"]],
    data_dict["intensity"][0:data_dict["length"]]
)
plt.ylabel('Intensity')
plt.xlabel('Wavelength / nm')
plt.show()

