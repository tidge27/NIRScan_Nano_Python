import hid
import time




def readCommand(device, group_byte, command_byte, data = []):
    bytes = [
        0x00, # ID Byte, set to 0
        0xC0, # Flags Byte 1100 0000  Read, wants a reply
        0x00, # Sequence Byte
        len(data) + 2, # Length of data (LSB)
        0x00, # Length of data (MSB) TODO: Include this in the length
        command_byte, # Command Byte
        group_byte  # Group Byte
    ]
    # Add the data bytes to the end of the list
    bytes.extend(data)

    # Start the read transaction
    device.write(bytes)

    # wait
    time.sleep(0.01)

    # read back the answer
    header = device.read(4)
    print("Command Requested By Host: ", "".join('{:02X}'.format(x) for x in header[0:1]))
    print("Response Length: {} bytes".format(header[2]))
    data_requested = device.read(header[2])

    return data_requested


def writeCommand(device, group_byte, command_byte, data = []):
    bytes = [
        0x00, # ID Byte, set to 0
        0x40, # Flags Byte 0100 0000  Write, wants a reply
        0x00, # Sequence Byte
        len(data) + 2, # Length of data (LSB)
        0x00, # Length of data (MSB) TODO: Include this in the length
        command_byte, # Command Byte
        group_byte  # Group Byte
    ]
    # Add the data bytes to the end of the list
    bytes.extend(data)

    # Start the write transaction
    device.write(bytes)

    # wait
    time.sleep(0.01)

    # read back the response
    header = device.read(4)

    return header