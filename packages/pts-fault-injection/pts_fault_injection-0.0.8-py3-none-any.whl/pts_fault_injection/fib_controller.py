import os
import can
import sys
import time
import logging
import cantools
from cantools.database.can.signal import NamedSignalValue

broadcast_id = 0x600
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
             16: "CMB Faults"
             }

dac_setpoints = [-1, -1, -1, -1, -1, -1, -1, -1]  # 8 DAC Channels
dac_mapping = {0: 9,
               1: 1,
               2: 5,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7}  # DAC Channel : Message Channel


def test_card(card):
    funcs = {
        "AnalogSignal": AnalogSignalCard.test_analog_signal_card,
        "StandardSignal1": StandardSignalCard.test_standard_signal_card1,
        "StandardSignal2": StandardSignalCard.test_standard_signal_card2,
        "StandardSignal3": StandardSignalCard.test_standard_signal_card3,
        "StandardSignal4": StandardSignalCard.test_standard_signal_card4,
        "BusSignal": BusSignalCard.test_bus_signal_card,
        "HVSignal": HVSignalCard.test_hv_signal_card,
        # "CellFault": self.test_cell_fault_board,
        # "LoadboxContactorCard": self.test_lb_contactor_card
    }
    if card in funcs:
        print(f"TESTING BOARD {card}")
        funcs[card]()
    else:
        raise Exception(f"Signal Card {card} not present.")


class FaultInjectionController(object):
    """
    Base class for the Fault Injection Box Controller
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, dbc_dir="../dbc/"):
        self.can_db = cantools.database.Database()
        self.bus = None
        logging.info(f"Searching for DBCs in {dbc_dir}")
        for file in os.listdir(dbc_dir):
            if file.endswith(".dbc"):
                logging.info(f"adding {file}")
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), dbc_dir + file))
        self.signal_cards = [
            StandardSignalCard(),
            StandardSignalCard(),
            StandardSignalCard(),
            StandardSignalCard(),
            AnalogSignalCard(),
            BusSignalCard(),
            SignalCard(),
            HVSignalCard(),
        ]
        return

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def read_FW_Response(self):
        time.sleep(1)
        wait_time = 1 + time.time()
        msg = self.bus.recv(timeout=1)
        rdy_IDs = []
        msg_buf = {}
        fw_versions = {}
        print("Searching for ready controllers.")
        while wait_time > time.time():
            if msg is not None and msg.dlc > 0:
                if 0x6FF > msg.arbitration_id > 0x600:
                    rdy_IDs.append(msg.arbitration_id)
                    msg_buf[msg.arbitration_id] = msg.data
                sys.stdout.write(".")
                sys.stdout.flush()
            msg = self.bus.recv(timeout=0.1)
        try:
            for id in rdy_IDs:
                fw_versions[id] = msg_buf[id].decode("ASCII")
        except Exception as e:
            raise Exception(f"\nError in finding FW versions for all responses {e}")
        return rdy_IDs, fw_versions

    def read_FW_Versions(self):
        # Writing FW Update Request
        logging.info("Using broadcast ID " + hex(broadcast_id))
        msg = can.Message(arbitration_id=broadcast_id, data=[ord('F'), ord('W'), ord('?'), 0, 0, 0, 0, 0],
                          is_extended_id=False)
        self.bus.send(msg)
        # Block until ready
        ids, fw_versions = self.read_FW_Response()
        for id in ids:
            try:
                logging.info("\nFW Information from board: " + board_ids[id - broadcast_id - 1] + " with FW version: "
                             + str(fw_versions[id]))
            except Exception as e:
                # pass
                raise Exception(f"ERR: Could not read FW version: {e}")
            return fw_versions

    def load_mapping(self):
        """
        This function loads the hil project specific signal mapping
        """
        return

    def set(self, channel, command, value):
        """
        Sets or unsets a command on a specific channel
        :param channel: int: channel number
        :param command:
        :param value: bool: set or unset the oc
        """
        [card, signal] = self.get_fib_card(channel)
        # get numer and send command
        data = self.signal_cards[card].get_command_for_msg(signal, command, value)
        self.send_relay_can_message(card, data, channel)

    def send_relay_can_message(self, card, data, channel):
        """
        creates a can message out of the state and sends it to the can connector

        CAN Message is RC_Cntrl , ID 0x210
        Signals :
            RC_mux -> fib Card (0-7) multiplexer
            RC_cntrlXX -> 60 Bit for the relays XX is multiplexer eg (01 or 00)
        """
        mux_name = "RC_cntrl" + str(card).zfill(2)

        cmd = {"RC_mux": card, mux_name: data, "chan": channel}
        self.send_can_message("RC_Cntrl", cmd)

    def send_can_message(self, msg_name, commands):
        try:
            cmd_message = self.can_db.get_message_by_name(msg_name)
        except Exception as e:
            print(f"ERROR: Message {msg_name} not found in Databases")
            print(e)
            return None

        # prepare a message with all signals
        signals = {}
        for signal in cmd_message.signals:
            if signal.name in commands:
                signals[signal.name] = commands[signal.name]
            else:
                signals[signal.name] = 0

        message = can.Message(arbitration_id=cmd_message.frame_id,
                              data=cmd_message.encode(signals, strict=False),
                              is_extended_id=False)
        logging.info(f"sending message {message}")
        self.bus.send(message)

    def get_fib_card(self, channel):
        """
        Calculates the FIB card number for a specific channel
        range 0-39 -> Standard signal card Id 10 steps
        range 40-49 -> Analog Signal card
        range 50-59 -> Bus Signal
        range 60-69 -> HV Signals
        Parameters
        ----------
        channel : int
            the channel to look for

        Returns
        -------
        int
            fib card number starting at 0

        """
        if channel in range(0, 70):
            return [channel // 10, channel % 10]
        else:
            return [-1, -1]


class SignalCard(object):
    """
    Base class for the Signal Cards
    """
    def __init__(self, dbc_dir="../dbc/"):
        self.bus = None
        self.can_db = cantools.database.Database()
        self.dbc_dir = dbc_dir
        print(f"Searching for DBCs in {self.dbc_dir}")
        for file in os.listdir(self.dbc_dir):
            if file.endswith(".dbc"):
                print(f"adding {file}")
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), self.dbc_dir + file))

        self.state = 0
        self.cmd_len = None

    def can_connection(self, interface, channel, bitrate):
        """
        Establishes a CAN connection
        :param interface: this usage with PEAK CAN Dongle
        :param channel: PCAN_USBBUS
        :param bitrate: 500000
        """
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()
        self.bus.flush_tx_buffer()  # Reset transmit after start

    def calculate_bit(self, signal, cmd, value):
        # calculate bit
        bit = cmd << signal * self.cmd_len

        if value:
            return self.state | bit  # make 'or' to switch on
        else:
            return self.state & ~bit  # make 'and' with negated to switch off

    def get_command_for_msg(self, signal, command, value):
        return None

    def parse_state(self):
        return None

    def send_can_message(self, msg_name, commands):
        try:
            cmd_message = self.can_db.get_message_by_name(msg_name)
        except Exception as e:
            print(f"ERROR: Message {msg_name} not found in Databases")
            print(e)
            return None

        # prepare a message with all signals
        signals = {}
        for signal in cmd_message.signals:
            if signal.name in commands:
                signals[signal.name] = commands[signal.name]
            else:
                signals[signal.name] = 0

        message = can.Message(arbitration_id=cmd_message.frame_id,
                              data=cmd_message.encode(signals, strict=False),
                              is_extended_id=False)
        logging.info(f"sending message {message}")
        self.bus.send(message)

    @staticmethod
    def print_bin(num):
        x = []
        for b in num:
            x.append(bin(b))
        print(x)

    @staticmethod
    def create_payload(card_id, relay_data):
        """
        This will create a list with 8 Data bytes (Total 64 Bits) to control HiL Cards
        Datastructure is as follows: (one based)
        Bit 1-4 -> Card ID
        Bit 5-64 -> Relay Data
        """
        out = [0] * 8
        out[0] = out[0] | (card_id & 0xF)
        out[0] = out[0] | (relay_data & 0xF) << 4
        for i in range(7):
            out[i + 1] = out[i + 1] | ((relay_data >> (i * 8) + 4) & 0xFF)
        return out

    def set_dac_value(self, channel, value):
        """Short summary.
        creates a can message out of the  dac state and sends it to the can connector

        CAN Message is DAC_BMS_Cntrl , ID 0x220
        Be aware of a weird channel mapping
        """
        dac_setpoints[channel] = value
        # Generate Signal name DAC_BMS_Cntrl_XX_YY_Voltage
        channel_msg = dac_mapping[channel] - 1
        dac_no = str(channel_msg // 4 + 1).zfill(2)  # Calculate Dac index, each dac has 4 channels
        ch_no = str((channel_msg % 4) + 1).zfill(2)  # channel is mod 4, both have to be filled to two digits
        mux = (0x10 * (channel_msg // 4)) + (channel_msg % 4)  # mux is 0-3 + 0x10 after each 4 channels
        cmd = {'DAC_BMS_Cntrl_Channel': mux, f"DAC_BMS_Cntrl_{dac_no}_{ch_no}_Voltage": value}
        self.send_can_message("DAC_BMS_Cntrl", cmd)

    def send_relay_can_message(self, card, data):
        mux_name = "RC_cntrl" + str(card).zfill(2)
        cmd = {'RC_mux': card, mux_name: data}
        self.send_can_message("RC_Cntrl", cmd)

    def send_relay_can_message_raw(self, card, data):
        message = can.Message(arbitration_id=528,
                              data=self.create_payload(card, data),
                              is_extended_id=False)
        self.bus.send(message)

    def check_card(self, card, relays=None):
        if card > 16:
            print(f"Card not there: {card}")
            return None
        if relays is None:
            max_relays = [32, 32, 32, 32, 48, 48, 32]  # max relays of cards
            relays = range(max_relays[card])
        if card == 4:  # analog card also set dac
            for ch in range(8):
                self.set_dac_value(ch, 2)
        for relay_no in relays:
            rly_set = 1 << (relay_no)
            print(f"Setting Card {card}, relay {relay_no}")
            print(bin(rly_set))
            self.send_relay_can_message_raw(card, rly_set)
            time.sleep(0.5)
            self.send_relay_can_message_raw(card, 0)
            time.sleep(0.1)


class StandardSignalCard(SignalCard):
    """Short summary.
    Standard Signal card has 10 Signals with the following functions:
        - Short to Chassis (SC)
        - Short to Faultrail
        - Open Circuit to out

    Mapping always signal*3 +
        - 0 for SC
        - 1 for Fault Rail
        - 2 for open circuit
    """

    def __init__(self):
        super().__init__()
        self.state = 0  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 3  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # Calculate command
        if command == "sc":
            cmd = 0b001
        elif command == "fr":
            cmd = 0b010
        elif command == "oc":
            cmd = 0b100
        else:
            print(f"Warning: {command} not accepted")
            return self.state

        return self.calculate_bit(signal, cmd, value)

    def parse_state(self):
        """Short summary.
        Returns a List with command to be set in CAN
        Returns
        Also here we need to shift by one if signal >= 5
        -------
        dict
            dict with data to be updated in CAN

        """
        def get_sig(sig, cmd):
            out = ((self.state >> (sig * self.cmd_len)) & cmd) > 0
            if sig >= 5:
                out = out >> 1
            return out

        out = {}
        for signal in range(self.signals):
            out[signal] = {"sc": get_sig(signal, 0b001),
                           "fr": get_sig(signal, 0b010),
                           "oc": get_sig(signal, 0b100)}
        return out

    def calculate_bit(self, signal, cmd, value):
        """
        Standard signal card uses not all channels of expander
        After the first 5 signals we need to shift by one bit
        Therefore shift by one bit if signal >= 5 (zero based )
        """
        bit = cmd << signal * self.cmd_len
        if signal >= 5:
            bit = bit << 1

        if value:
            return self.state | bit  # make 'or' to switch on
        else:
            return self.state & ~bit  # make 'and' with negated to switch off

    def test_standard_signal_card1(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(0, used_ports)

    def test_standard_signal_card2(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(1, used_ports)

    def test_standard_signal_card3(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(2, used_ports)

    def test_standard_signal_card4(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(3, used_ports)


class AnalogSignalCard(SignalCard):
    """
    Analog Signal card has 8 Signals with the following functions:
        - Short to Chassis (SC)
        - Short to Fault Rail
        - Connect DAC Output
        - Open Circuit to out

    And 2 signals that are resistor signals with the following functions:
        - Short to Chassis (SC)
        - Short to Fault Rail
        - Resistor 12R
        - Resistor 24R
        - Resistor 51R
        - Resistor 100R
        - Open Circuit to out

    Mapping always signal*4 +
        - 0 for SC
        - 1 for Fault Rail
        - 2 for Connect dac
        - 3 for open circuit
    """

    def __init__(self):
        super().__init__()
        self.bus = self.bus
        self.state = 0  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 4  # amount of usable functions on card
        return

    def parse_state(self):
        """Short summary.
        Returns a List with command to be set in CAN
        Returns
        -------
        dict
            dict with data to be updated in CAN

        """

        def get_sig(sig, cmd):
            return ((self.state >> (sig * 4)) & cmd) > 0

        out = {}
        for signal in range(0, 8):
            out[signal] = {"sc": get_sig(signal, 0b0001),
                           "fr": get_sig(signal, 0b0010),
                           "dac": get_sig(signal, 0b0100),
                           "oc": get_sig(signal, 0b1000)
                           }
        for signal in range(8, self.signals):
            out[signal] = {"sc": get_sig(signal, 0b0000001),
                           "fr": get_sig(signal, 0b0000010),
                           "r12": get_sig(signal, 0b0000100),
                           "r24": get_sig(signal, 0b0001000),
                           "r51": get_sig(signal, 0b0010000),
                           "r100": get_sig(signal, 0b0100000),
                           "oc": get_sig(signal, 0b1000000)
                           }
        return out

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # calculate command
        elif signal in range(0, 8):
            if command == "sc":
                cmd = 0b0001
            elif command == "fr":
                cmd = 0b0010
            elif command == "dac":
                cmd = 0b0100
            elif command == "oc":
                cmd = 0b1000
        elif signal in range(8, self.signals):
            if command == "sc":
                cmd = 0b0000001
            elif command == "fr":
                cmd = 0b0000010
            elif command == "r12":
                cmd = 0b0000100
            elif command == "r24":
                cmd = 0b0001000
            elif command == "r51":
                cmd = 0b0010000
            elif command == "r100":
                cmd = 0b0100000
            elif command == "oc":
                cmd = 0b1000000

        elif command == "dac_voltage":
            if signal in range(0, 7):
                self.set_dac_value(signal, float(value))
                return self.state
        else:
            print(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)

    def test_analog_signal_card(self):
        used_ports = list(range(39)) + list(range(40, 48))  # zero based
        self.check_card(4, used_ports)


class BusSignalCard(SignalCard):
    """
    Bus Signal card has 12 Signals with the following functions:
        - Fault Rail 2 (First Bit)
        - Fault Rail 1 (second Bit)
        - Additional Input (third bit)
        - Open Circuit (fourth bit)
    """

    def __init__(self):
        super().__init__()
        self.bus = self.bus
        self.state = 0  # Todo get initial state from status message
        self.signals = 12
        self.cmd_len = 4  # amount of usable functions on card
        return

    def parse_state(self):
        """
        Returns a List with command to be set in can
        :return dict: dict with data to be updated in can
        """

        def get_sig(sig, cmd):
            return ((self.state >> (sig * 4)) & cmd) > 0

        out = {}
        for signal in range(0, 12):
            out[signal] = {"fr2": get_sig(signal, 0b0001),
                           "fr1": get_sig(signal, 0b0010),
                           "in": get_sig(signal, 0b0100),
                           "oc": get_sig(signal, 0b1000)
                           }
        return out

    def get_command_for_msg(self, signal, command, value):
        cmd = {}
        # Check if channel is in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # calculate command
        elif signal in range(0, self.signals):
            if command == "fr2":
                cmd = 0b0001
            elif command == "fr1":
                cmd = 0b0010
            elif command == "in":
                cmd = 0b0100
            elif command == "oc":
                cmd = 0b1000
        else:
            print(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)

    def test_bus_signal_card(self):
        used_ports = list(range(3 * 16))  # zero based
        self.check_card(5, used_ports)


class HVSignalCard(SignalCard):
    """
    HV Signal card has 8 HV Signals with the following functions:
        - Short to Chassis (SC) via resistor
        - Open Circuit
    There are also 2 Channels for ISOSPI Connection which allow Open Circuit
    Channel 1-8 -> HV
    Channel 9,10 -> ISOSPI
    """

    def __init__(self):
        super().__init__()
        # Initial State is complicated. All first 16 Bits are 'on'
        # On the second 16 Bit we need to switch on only every second
        self.bus = self.bus
        self.state = int(b"01010101010101011111111111111111", 2)  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 2  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # Calculate command
        if command == "oc":
            cmd = 0b01
        elif command == "sc":
            cmd = 0b10
        else:
            print(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)

    def parse_state(self):
        """
        Returns a List with command to be set in CAN
        Returns
        Also here we need to shift
        BE careful as signals for HV Card are inverted
        -------
        dict
            dict with data to be updated in can

        """

        def get_sig(sig, cmd):
            if sig >= 8:
                return ((self.state >> ((sig - 8) * self.cmd_len)) & ~cmd) > 0
            if sig < 8:
                return ((self.state >> (16 + sig * self.cmd_len)) & cmd) > 0
            return out

        out = {}
        for signal in range(self.signals):
            out[signal] = {
                "oc": get_sig(signal, 0b001),
                "sc": get_sig(signal, 0b010),
            }
        return out

    def calculate_bit(self, signal, cmd, value):
        """
        HV signal card uses not all channels of expander the first expander
        is connected to ISOSPI channels. second one is for HV Signals
        Therefore shift by 16 bits if signal <8 (zero based )
        """
        if signal >= 8:
            bit = cmd << ((signal - 8) * self.cmd_len)
        else:
            bit = cmd << ((signal * self.cmd_len) + 16)

        # HV OC Signals are reed relays and need and are inverted -> On is not SC, Off is SC
        # HV SC Signals are not inverted, so we need to distinguish
        if value:
            if cmd == 0b01:
                return self.state & ~bit  # make 'or' to switch on
            else:
                return self.state | bit  # make 'or' to switch on
        else:
            if cmd == 0b01:
                return self.state | bit  # make 'and' with negated to switch off
            else:
                return self.state & ~bit  # make 'and' with negated to switch off

    def test_hv_signal_card(self):
        used_ports = list(range(4)) + list(range(16, 32))  # zero based
        self.check_card(6, used_ports)

