#NIR Scan Nano Python Driver
This is a WIP of a driver to support taking a scan using the NIR Nano spectrometer by TI

##Notes and References
For information on the scan workflow; look at section 5.2.1 of the DLP® NIRscan™ Nano EVM User's Guide.

For information on the USB commands; refer to section H.1 of the DLP® NIRscan™ Nano EVM User's Guide.

Details on `ctrl_transfer` in the `PyUSB` library: https://www.beyondlogic.org/usbnutshell/usb6.shtml#SetupPacket

Details on writing / reading: https://stackoverflow.com/questions/29345325/raspberry-pyusb-gets-resource-busy

USB communication example for another product using python/PyUSB: https://github.com/respeaker/respeaker_python_library/blob/master/respeaker/usb_hid/pyusb_backend.py 