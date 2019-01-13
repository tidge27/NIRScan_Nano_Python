import ctypes
import time

dlp_nano_lib = ctypes.CDLL("/Users/thomasgarry/ti/DLPSpectrumLibrary_2.0.2/src/libtest.dylib")

class calibCoeffs(ctypes.Structure):
    _fields_ = [
        ("ShiftVectorCoeffs", ctypes.c_double*3),
        ("PixelToWavelengthCoeffs", ctypes.c_double * 3),
    ]

class slewScanSection(ctypes.Structure):
    _fields_ = [
        ("section_scan_type", ctypes.c_uint8),
        ("width_px", ctypes.c_uint8),
        ("wavelength_start_nm", ctypes.c_uint16),
        ("wavelength_end_nm", ctypes.c_uint16),
        ("num_patterns", ctypes.c_uint16),
        ("exposure_time", ctypes.c_uint16)
    ]

class slewScanConfigHead(ctypes.Structure):
    _fields_ = [
        ("scan_type", ctypes.c_uint8),
        ("scanConfigIndex", ctypes.c_uint16),
        ("ScanConfig_serial_number", ctypes.c_char*8),
        ("config_name", ctypes.c_char*40),
        ("num_repeats", ctypes.c_uint16),
        ("num_sections", ctypes.c_uint8)
    ]

class slewScanConfig(ctypes.Structure):
    _fields_ = [
        ("head", slewScanConfigHead),
        ("section", slewScanSection*5)
    ]




class scanResults(ctypes.Structure):
    _fields_ = [
        ("header_version", ctypes.c_uint32),
        ("scan_name", ctypes.c_char * 20),
        ("year", ctypes.c_uint8),
        ("month", ctypes.c_uint8),
        ("day", ctypes.c_uint8),
        ("day_of_week", ctypes.c_uint8),
        ("hour", ctypes.c_uint8),
        ("minute", ctypes.c_uint8),
        ("second", ctypes.c_uint8),
        ("system_temp_hundredths", ctypes.c_int16),
        ("detector_temp_hundredths", ctypes.c_int16),
        ("humidity_hundredths", ctypes.c_uint16),
        ("lamp_pd", ctypes.c_uint16),
        ("scanDataIndex", ctypes.c_uint32),
        ("calibration_coeffs", calibCoeffs),
        ("serial_number", ctypes.c_char),
        ("adc_data_length", ctypes.c_uint16),
        ("black_pattern_first", ctypes.c_uint8),
        ("black_pattern_period", ctypes.c_uint8),
        ("pga", ctypes.c_uint8),
        ("cfg", slewScanConfig),
        ("wavelength", ctypes.c_double * 864),
        ("intensity", ctypes.c_int * 864),
        ("length", ctypes.c_int)
    ]


dlp_nano_lib.dlpspec_scan_interpret.argtypes = [ctypes.POINTER(ctypes.c_char*3822), ctypes.c_size_t, ctypes.POINTER(scanResults)]

dlp_nano_lib.dlpspec_scan_slew_get_end_nm.argtypes = [ctypes.POINTER(slewScanConfig)]


results = scanResults()
print(results)
res_pointer = ctypes.byref(results)
print(res_pointer)

byte_input_list = []


with open("binary.dat", "rb") as binaryfile:
    myArr = bytearray(binaryfile.read())
for byte in myArr:
    byte_input_list.append(byte)
print(byte_input_list)
byte_input_list = byte_input_list[:int(len(byte_input_list)/2)]
print(byte_input_list)
byte_file = bytearray(byte_input_list)
print(byte_file)


buffer = ctypes.create_string_buffer(3822)
for counter, byte in enumerate(byte_input_list):
    buffer[counter] = byte
# buffer[0] = 116
print(buffer[0])

buffer_pointer = ctypes.pointer(buffer)

size_number = ctypes.c_size_t(len(byte_file))
print(size_number)

# time.sleep(1)
dlp_nano_lib.dlpspec_scan_interpret(buffer_pointer, size_number, res_pointer)

print(results.scan_name)
# def our_function(numbers):
#     global _sum
#     num_numbers = len(numbers)
#     array_type = ctypes.c_int * num_numbers
#     result = _sum.our_function(ctypes.c_int(num_numbers), array_type(*numbers))
#     return int(result)