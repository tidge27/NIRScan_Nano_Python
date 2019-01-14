# NIR Scan Nano Python Driver
This is a WIP of a driver to support taking a scan using the NIR Nano spectrometer by TI

## Usage
In order to use these scripts, the DLPSpectrumLibrary will need to be installed, and compiled.  These python scripts require a dynamic library to be compiled, which is then wrapped using the python ctypes library. 
This dynamic library can be compiled using the following steps on MacOS
```
gcc -c -DTPL_NOLIB -Wall dlpspec.c dlpspec_scan.c dlpspec_calib.c dlpspec_util.c tpl.c dlpspec_scan_col.c dlpspec_scan_had.c dlpspec_helper.c
clang -dynamiclib -o libtest.dylib dlpspec.o dlpspec_scan.o dlpspec_calib.o dlpspec_util.o tpl.o dlpspec_scan_had.o dlpspec_scan_col.o dlpspec_helper.o
rm *.o
```
Currently, the full path is referred to in test_dll.py
#### File Breakdown
usb.py - Handles read and writes to the spectrometer using the NIRscan USB protocol

scan.py - Completes a scan on the spectrometer

test_dll.py - converts the .dat from scan.py into a json object.
## Notes and References
For information on the scan workflow; look at section 5.2.1 of the DLP® NIRscan™ Nano EVM User's Guide.

For information on the USB commands; refer to section H.1 of the DLP® NIRscan™ Nano EVM User's Guide.

Details on `ctrl_transfer` in the `PyUSB` library: https://www.beyondlogic.org/usbnutshell/usb6.shtml#SetupPacket

Details on writing / reading: https://stackoverflow.com/questions/29345325/raspberry-pyusb-gets-resource-busy

USB communication example for another product using python/PyUSB: https://github.com/respeaker/respeaker_python_library/blob/master/respeaker/usb_hid/pyusb_backend.py 

Cython HIDAPI:
https://github.com/trezor/cython-hidapi
After much experimentation, this has been used instead of PyUSB.  This library works on MacOS, and provides a more simple interface with the HID device type.
