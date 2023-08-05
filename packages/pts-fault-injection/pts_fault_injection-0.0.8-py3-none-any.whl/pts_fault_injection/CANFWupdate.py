import can
import time
import logging
import sys
import urllib.request
import xml.dom.minidom

board_ids = {0: "Standard Signals 1",
             1: "Standard Signals 2",
             2: "Standard Signals 3",
             3: "Standard Signals 4",
             4: "Analog Signals",
             5: "Bus Signals",
             6: "HV Signals",
             9: "Contactor Card",
             10: "HV Box Card",
             14: "DAC Board",
             15: "Break Out Box",
             16: "CMB Faults",
             0x20: "BMS DAC",
             0x21: "CMB DAC 1",
             0x22: "CMB DAC 2",
             0x24: "CMB DAC 3",
             0x25: "CMB DAC 4",
             0x26: "CMB DAC 5",
             0x27: "CMB DAC 6"
             }


def read_until_Y():
    msg = bus.recv(timeout=2)
    # logger.debug(msg)
    while True:
        if msg != None and msg.dlc > 0:
            if msg.data[0] == 89:
                break
        logger.debug(msg)
        msg = bus.recv(timeout=2)


def read_until_all_Y(IDs):
    received_y_ids = []
    wait_time = 5 + time.time()
    msg = bus.recv(timeout=1)
    # logger.debug(msg)
    while wait_time > time.time():
        if msg != None and msg.dlc > 0:
            if msg.data[0] == 89 and (msg.arbitration_id in IDs):
                received_y_ids.append(msg.arbitration_id)
            if all(x in received_y_ids for x in IDs):
                logger.debug(f"Got acknowledge from {len(received_y_ids)}")
                return 0  # ALL OK !
        msg = bus.recv(timeout=1)
    logger.error(f"Missing a ready from required controller in {ids} {received_y_ids}")
    return -1  # ERROR NOT ALL BOARDS RESPONDING


def read_until_RDY():
    wait_time = 2 + time.time()
    msg = bus.recv(timeout=2)
    # logger.debug(msg)
    rdy_IDs = []
    msg_buf = {}
    fw_versions = {}
    print("Searching for ready controllers.")
    while wait_time > time.time():
        if msg != None and msg.dlc > 0:
            if (chr(msg.data[0]) == 'R' and chr(msg.data[1]) == 'D' and chr(msg.data[2]) == 'Y' and chr(
                    msg.data[3]) == '!'):
                rdy_IDs.append(msg.arbitration_id)
                logger.debug(msg)
            else:
                msg_buf[msg.arbitration_id] = msg.data

        sys.stdout.write(".")
        sys.stdout.flush()
        msg = bus.recv(timeout=1)
    try:
        for id in rdy_IDs:
            fw_versions[id] = msg_buf[id].decode("ASCII")
    except:
        print("\nError in finding FW versions for all responses")
    return rdy_IDs, fw_versions


def send_can_line(line, broadcast_id):
    msg = can.Message(arbitration_id=broadcast_id, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
    idx = 0
    for elem in line:
        if idx >= 8:
            # print(msg)
            bus.send(msg)
            msg = can.Message(arbitration_id=broadcast_id, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            idx = 0
        msg.data[idx] = elem
        idx += 1
    # print(msg)
    bus.send(msg)


def send_hex_file(filepath, IDs, broadcast_id):
    # Writing Hex File
    num_lines = sum(1 for line in open(filepath))
    with open(filepath) as file:
        line = file.readline()
        cnt = 0
        while line:
            sys.stdout.write("\rWriting " + str(round(cnt / num_lines * 100)) + "%")
            sys.stdout.flush()
            # logger.debug("Writing line " + str(cnt))
            # line =line + "\n"
            send_can_line(line.encode(), broadcast_id)
            if read_until_all_Y(IDs) < 0:
                print("ERROR in receiving acknowledge from Boards, rebooting accessible boards")
                send_can_line(":reboot\n".encode(), broadcast_id)
                return -1
            time.sleep(0.005)
            line = file.readline()
            cnt += 1
    return cnt


def parse_s3_index_response(xml):
    keys = dom.getElementsByTagName('Key')
    files = []
    for key in keys:
        files.append(key.firstChild.nodeValue)
    return files


###########################
####### Setup Script#######
###########################
# Set to True if you want to create a logfile
create_log_file = False

# Configure PEAK CAN interface PCAN Mac library has to be installed
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS1'
can.rc['bitrate'] = 500000
bus = can.interface.Bus()

# Setup Can filters for safe interaction and flush buffer
bus.flush_tx_buffer()
filters = [{'can_mask': 0x700, 'can_id': 0x600}]
bus.set_filters(filters)

# create logger with 'flasher_application'
logger = logging.getLogger('flasher')
logger.setLevel(logging.WARNING)
# create file handler which logs even debug messages
t = time.strftime("%Y%m%d-%H%M%S")
if create_log_file:
    fh = logging.FileHandler('spam' + t + '.log')
    fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if create_log_file:
    fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
if create_log_file:
    logger.addHandler(fh)
logger.addHandler(ch)

#####################
#### Run Script ####
#####################
# Define Interface and Hexfile from agrv
if len(sys.argv) == 2:
    filepath = str(sys.argv[1])
else:
    print("You Have not specified an input HEX file\nDo you want to download one from the Internet? (Y/N)")
    res = input()
    while res not in ('Y', 'N'):
        print("Could not interpret the input, try again or cancel with ctrl-c")
        res = input()
    if res == 'Y':
        with urllib.request.urlopen('http://hil-common-firmware.s3.us-east-2.amazonaws.com/?list-type=2') as response:
            dom = xml.dom.minidom.parseString(response.read())
            files = parse_s3_index_response(dom)

        print("Following Files have been found Online:")
        idx = 1
        for file in files:
            print(str(idx) + " - " + str(file))
            idx += 1

        print("Please choose file to Download")
        file_idx = int(input())

        urllib.request.urlretrieve(
            'http://hil-common-firmware.s3-website.us-east-2.amazonaws.com/' + files[file_idx - 1], 'firmware.hex')
        filepath = "firmware.hex"

broadcast_id = 0x600
print("Using broadcast ID " + hex(broadcast_id))
# Writing FW Update Request
msg = can.Message(arbitration_id=broadcast_id, data=[ord('U'), ord('P'), ord('D'), 0, 0, 0, 0, 0], is_extended_id=False)
bus.send(msg)
# Block until ready
ids, fw_versions = read_until_RDY()
str_id = []

for id in ids:
    try:
        print("\nReceived RDY! from board: " + board_ids[id - broadcast_id - 1] + " with FW version: " + str(
            fw_versions[id]))
    except:
        print("\nReceived RDY! from following ID: " + hex(id))

print("Do you want to proceed(Y)? or Exit and Reboot(R))")
res = input()
while res not in ('Y', 'R'):
    print("Could not interpret the input, try again")
    res = input()

if res == 'R':
    print("trying to reboot devices and exiting....")
    send_can_line(":reboot\n".encode(), broadcast_id)
else:
    # Proceed!
    # Write Hex File
    print("Writing hexfile " + filepath)
    linecount = send_hex_file(filepath, ids.copy(), broadcast_id)
    # Writing FW Flash Command
    print("\nWriting Flash Command")
    time.sleep(1)
    cmd = ":flash " + str(linecount) + "\n"
    send_can_line(cmd.encode(), broadcast_id)
    time.sleep(1)
    send_can_line(cmd.encode(), broadcast_id)
    # if read_until_all_Y(ids) < 0:
    #    logging.error("ERROR in receiving flash acknowledge from Boards, rebooting accessible boards")
    send_can_line(":reboot\n".encode(), broadcast_id)
