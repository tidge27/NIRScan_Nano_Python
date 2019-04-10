import os
import asyncio
import CissUsbConnectord
import time
import hid
import logging
import platform
import threading
from threading import Thread
import pylink
from collections import deque


from scan import Spectrometer, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
from spectrum_library import scan_interpret



def setup_print():
    # Settings for the print recording session
    directory_index = 10
    root_folder_name  = "sesame-" + str(directory_index).zfill(16)
    measurements_folder_name = "Measurements"


    sensor_directories = {
        'CISS': "L0",
        'Spectrometer': "L1"
    }

    # Set the data location for the CISS data
    CissUsbConnectord.data_file_folder = os.path.join(
        root_folder_name,
        measurements_folder_name,
        sensor_directories['CISS']
    )

    # set the folder for the spectrometer data
    global spectrometer_folder
    spectrometer_folder = os.path.join(
        root_folder_name,
        measurements_folder_name,
        sensor_directories['Spectrometer']
    )




    # Create the file structure
    if os.path.isdir(root_folder_name):
        logging.error("Directory `{}` already exists.  Please change the directory index for the build you wish to start".format(root_folder_name))
        exit()
    else:
        for sensor, directory in sensor_directories.items():
            structure = os.path.join(root_folder_name, measurements_folder_name, directory)
            os.makedirs(structure)


    logPath = root_folder_name

    logFileName = "print_log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler("{0}/{1}.log".format(logPath, logFileName)),
            logging.StreamHandler()
        ]
    )


    logging.info("Start Timestamp : {}".format(str(int(time.time()*1000))))
    logging.info(platform.machine())
    logging.info(platform.version())
    logging.info(platform.platform())
    logging.info(platform.uname())
    logging.info(platform.system())
    logging.info(platform.processor())



def read_spectrometer_save(spectrometer, folder):
    # TODO: chnage the handling of exceptions in the spectrometer class

    # Get timestamp at the start of the spectrometer reading
    scan_start_timestamp = int(time.time() * 1000)

    try:

        # Do scan
        spectrometer.perform_scan()
        # Get scan data
        scan_data = spectrometer.get_file(NNO_FILE_SCAN_DATA)
        # Get calibration data
        reference_data = spectrometer.get_file(NNO_FILE_REF_CAL_COEFF)
    except OSError:
        logging.warning("Something has gone wrong with the Spectrometer Will attempt to reconnect soon")
        while(not spectrometer.reconnect_device()):
            time.sleep(1)
        return

    if(not(scan_data and reference_data)):
        return
    # combine the data and save the dat file (readable by the GUI program provided by TI)
    byte_file_combined = bytearray(scan_data + reference_data)

    # Setup the file names for the JSON data
    dat_file_name = "spectrometer_reading_{}.dat".format(str(scan_start_timestamp).zfill(14))
    json_file_name = "spectrometer_reading_{}.JSON".format(str(scan_start_timestamp).zfill(14))
    # Write the dat file (in the format provided by the TI GUI
    scan_dat_file = open(os.path.join(folder, dat_file_name), "wb")
    scan_dat_file.write(byte_file_combined)
    # Interpret the data to JSON object
    json_formatted_data = scan_interpret(scan_data)
    # Save the data in a .JSON file
    scan_json_file = open(os.path.join(folder, json_file_name), "w")
    scan_json_file.write(json_formatted_data)

# start logging

def start_ciss_log(running, folder, com_port):
    try:
        logging.info("Opening the CISS device")
        node = CissUsbConnectord.CISSNode(folder, com_port)
    except Exception as ex:
        logging.warning("CISS device not found")
        node = None
        # return

    while(running.is_set()):
        if node:
            try:
                node.stream()
            except Exception as error:
                logging.warning("the CISS has been disconnected!")
                node = None
        else:
            try:
                time.sleep(1)
                node = CissUsbConnectord.CISSNode(folder)
                logging.info("Connected to the CISS device")
            except Exception as ex:
                node = None


def start_spectrometer_log(running, folder, serial_no=None):

    spectrometer = Spectrometer(0x0451, 0x4200, serial_no)

    while(running.is_set()):
        time.sleep(5)
        read_spectrometer_save(spectrometer, folder)

def start_seggr_log(running, folder):
    target_device = "MKL03Z32XXX4"
    jlink = pylink.JLink()
    line_count = 0
    while (running.is_set()):
        print("connecting to JLink...")
        jlink.open()
        print("connecting to %s..." % target_device)
        jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        jlink.connect(target_device)
        print("connected, starting RTT...")
        jlink.rtt_start()

        while True:
            try:
                num_up = jlink.rtt_get_num_up_buffers()
                num_down = jlink.rtt_get_num_down_buffers()
                print("RTT started, %d up bufs, %d down bufs." % (num_up, num_down))
                break
            except pylink.errors.JLinkRTTException:
                time.sleep(0.1)

        try:
            character_buffer = deque()
            while jlink.connected():
                terminal_bytes = jlink.rtt_read(0, 1024)
                if terminal_bytes:
                    characters = map(chr, terminal_bytes)
                    character_buffer.extend(characters)
                    while(1):
                        try:
                            end_line = character_buffer.index('\n')
                            line_count += 1
                            # TODO change this 3 to something more sensible than 3 lines!!!
                            file = os.path.join(folder, "stream-{}.csv".format(int(line_count/3)))
                            with open(file, "a") as stream_file:
                                for char_index in range(0,end_line):
                                    stream_file.write(character_buffer.popleft())

                        except ValueError as error:
                            # No newlines found yet
                            break
                    # sys.stdout.flush()
                    pass
                    # sys.stdout.write("".join(map(chr, terminal_bytes)))
                    # sys.stdout.flush()
                time.sleep(0.01)
            print("JLink disconnected, exiting...")
        except Exception:
            logging.error("something with warp went wrong :'(")


def main():
    run_event = threading.Event()
    run_event.set()

    ciss_log = Thread(target=start_ciss_log, args=[run_event])
    spectrometer_log = Thread(target=start_spectrometer_log, args=[run_event, spectrometer_folder])
    ciss_log.start()
    spectrometer_log.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close threads. Max wait = 10s")
        run_event.clear()
        ciss_log.join()
        spectrometer_log.join()
        print("threads successfully closed")


if __name__ == '__main__':
    setup_print()
    main()

