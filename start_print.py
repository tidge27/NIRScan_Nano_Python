import os
import asyncio
import CissUsbConnectord
import time
import hid
import logging

from scan import get_file, perform_scan, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
from spectrum_library import scan_interpret

# Settings for the print recording session
directory_index = 2
root_folder_name  = "sesame-" + str(directory_index).zfill(16)
measurements_folder_name = "Measurements"


sensor_directories = {
    'CISS': "L0",
    'Spectrometer': "L1"
}

# Set the data location for the CISS data
CissUsbConnectord.dataFileLocation = os.path.join(
    root_folder_name,
    measurements_folder_name,
    sensor_directories['CISS'],
    "CISS_measurements.csv"
)

# set the folder for the spectrometer data
spectrometer_folder = os.path.join(
    root_folder_name,
    measurements_folder_name,
    sensor_directories['Spectrometer']
)


# Create the file structure
if os.path.isdir(root_folder_name):
    print("Directory `{}` already exists.  Please change the directory index for the build you wish to start".format(root_folder_name))
    exit()
else:
    for sensor, directory in sensor_directories.items():
        structure = os.path.join(root_folder_name, measurements_folder_name, directory)
        os.makedirs(structure)




def read_spectrometer_save(h):

    # disable non-blocking mode, makes life easier, sacrifices speed
    h.set_nonblocking(0)
    # Get timestamp at the start of the spectrometer reading
    scan_start_timestamp = int(time.time() * 1000)
    # Do scan
    perform_scan(h)
    # Get scan data
    scan_data = get_file(h, NNO_FILE_SCAN_DATA)
    # Get calibration data
    reference_data = get_file(h, NNO_FILE_REF_CAL_COEFF)

    # combine the data and save the dat file (readable by the GUI program provided by TI)
    byte_file_combined = bytearray(scan_data + reference_data)

    # Setup the file names for the JSON data
    dat_file_name = "spectrometer_reading_{}.dat".format(str(scan_start_timestamp).zfill(14))
    json_file_name = "spectrometer_reading_{}.JSON".format(str(scan_start_timestamp).zfill(14))
    # Write the dat file (in the formatt provided by the TI GUI
    scan_dat_file = open(os.path.join(spectrometer_folder, dat_file_name), "wb")
    scan_dat_file.write(byte_file_combined)
    # Interpret the data to JSON object
    json_formatted_data = scan_interpret(scan_data)
    # Save the data in a .JSON file
    scan_json_file = open(os.path.join(spectrometer_folder, json_file_name), "w")
    scan_json_file.write(json_formatted_data)

import random
def take_reading():
    print("Starting reading", str(time.time()))
    start_time = time.time()
    while time.time() < start_time + 10:
        random.randint(1000, 2000)
    print("Reading complete", str(time.time()))

# start logging

async def start_ciss_log():
    try:
        logging.info("Opening the CISS device")
        node = CissUsbConnectord.CISSNode()
    except Exception as ex:
        logging.warning("CISS device not found")
        return

    while(1):
        node.stream()


async def start_spectrometer_log():

    # h = hid.device()
    # try:
    #     logging.info("Opening the spectrometer HID device")
    #     h.open(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
    # except IOError as ex:
    #     logging.warning("NIRScan Nano not found")
    #     return

    while(1):
        take_reading()
        # read_spectrometer_save(h)
        await asyncio.sleep(5)
    pass


async def main():
    await asyncio.gather(
        start_ciss_log(),
        start_spectrometer_log()
    )


asyncio.run(main())