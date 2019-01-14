from scan import get_file, perform_scan, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
import hid
from test_dll import scan_interpret

# Try to open the device, otherwise read in file data
h = hid.device()
device_open = True
try:
    print("Opening the device")
    h.open(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
except IOError as ex:
    print(ex)
    print("Looks like the NIRScan Nano isn't connected")
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
    newFile = open("output.dat", "wb")
    newFile.write(byte_file_combined)
else:
    # Open the binary
    with open("binary.dat", "rb") as binaryfile:
        myArr = bytearray(binaryfile.read())
    # send the first half through to the interpret function
    scan_data = myArr[0:int(len(myArr)/2)]

# Interpret data
print(scan_interpret(scan_data))