import ctypes
import json


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

dlp_nano_lib = ctypes.CDLL("/Users/thomasgarry/ti/DLPSpectrumLibrary_2.0.2/src/libtest.dylib")
dlp_nano_lib.dlpspec_scan_interpret.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(scanResults)]


def unpack_fields(result_in):
    dict = {}
    for field_name, field_type in result_in._fields_:
        try:
            dict[field_name] = unpack_fields(getattr(result_in, field_name))
        except Exception as error:
            value = getattr(result_in, field_name)

            if type(value) == type(bytes()):
                value = value.decode("utf-8")
            elif type(value) not in [type(int()), type(float)]:
                newval = []
                for i in value:
                    try:
                        newval.append(unpack_fields(i))
                    except Exception as error:
                        newval.append(i)
                value = newval
            dict[field_name] = value
    return dict


def scan_interpret(myArr):

    byte_input_list = []
    for byte in myArr:
        byte_input_list.append(byte)

    # Initialise the input data buffer
    buffer = ctypes.create_string_buffer(len(byte_input_list))
    for counter, byte in enumerate(byte_input_list):
        buffer[counter] = byte
    # Create the pointer to the buffer
    buffer_pointer = ctypes.pointer(buffer)

    # Create the size variable
    size_number = ctypes.c_size_t(len(byte_input_list))

    # Create the results variable
    results = scanResults()
    # Create the pointer to the results
    res_pointer = ctypes.byref(results)

    # Run the library fucntion
    dlp_nano_lib.dlpspec_scan_interpret(buffer_pointer, size_number, res_pointer)

    # unpack the results
    unpacked = unpack_fields(results)

    return json.dumps(unpacked)

