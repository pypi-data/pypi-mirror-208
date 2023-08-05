import logging
import can
import time
import cantools
from cantools.database.can.signal import NamedSignalValue

dac_setpoints = [-1, -1, -1, -1, -1, -1, -1, -1]  # 8 DAC Channels

dac_mapping = {0: 9,
               1: 1,
               2: 5,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7}  # DAC Channel : Message Channel


def get_bit(number, position):
    return number >> position & 1


class ContactorBoard:

    def __init__(self):
        """
        Initialization for Contactor Fault Class
        """
        self.can_db = cantools.database.Database()
        self.bus = None
        self.state = {}
        self.contactors = 10  # amount of contactor channels on board
        self.shorts = 3  # amount of short channels
        self.contactor_state = {}
        self.short_state = {}
        for contactor in range(self.contactors):
            self.contactor_state[contactor] = {"weld": 0, "stuck_open": 0}
        for short in range(self.shorts):
            self.short_state[short] = {"active": 0}

        return

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def set(self, device, channel, function, type, value):
        try:
            if type == "SET":
                if device == "CONTACTOR_FAULTS" and channel in self.contactor_state:
                    if type in self.contactor_state[channel]:
                        self.contactor_state[channel][function.lower()] = bool(int(value))
                if device == "SHORTS" and channel in self.short_state:
                    self.short_state[channel]["active"] = bool(int(value))
        except Exception as e:
            print(f"Error in setting fault {function} for channel {channel} with value {value}, {e}")
        self.send_state_to_board()

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
        for relay_no in relays:
            rly_set = 1 << (relay_no)
            print(f"Setting Card {card}, relay {relay_no}")
            print(bin(rly_set))
            self.send_relay_can_message_raw(card, rly_set)
            time.sleep(0.5)
            self.send_relay_can_message_raw(card, 0)
            time.sleep(0.1)

    def send_state_to_board(self):
        bytes = 0
        for signal in self.contactor_state:
            chip_offset = (signal // 8) * 16  # calculate the offset after 8 Signals
            bytes = bytes | (bool(self.contactor_state[signal]["weld"]) << (signal + chip_offset))
            bytes = bytes | (bool(self.contactor_state[signal]["stuck_open"]) << (8 + signal + chip_offset))
        for signal in self.short_state:
            bytes = bytes | (bool(self.short_state[signal]["active"]) << (18 + signal))

        self.send_relay_can_message(bytes)

    def parse_can_state(self, can_state):
        for signal in self.contactor_state:
            # calculate the offset after 8 Signals
            chip_offset = (signal // 8) * 16
            self.contactor_state[signal]["weld"] = get_bit(can_state, signal + chip_offset)
            self.contactor_state[signal]["stuck_open"] = get_bit(can_state, 8 + signal + chip_offset)
        for signal in self.short_state:
            bytes = bytes | (bool(self.short_state[signal]["active"]) << (18 + signal))

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

    def send_relay_can_message(self, data):
        """Short summary.
        creates a can message out of the state and sends it to the can connector

        CAN Message is RC_Cntrl , ID 0x210
        Signals :
            RC_mux -> fib Card (9) multiplexer
            RC_cntrlXX -> 60 Bit for the relays XX is mutliplexer eg (01 or 00)
        """
        mux_name = "RC_cntrl09"

        cmd = {'RC_mux': 9, mux_name: data}
        self.send_can_message(f"RC_Cntrl", cmd)

    # def update_state(self, status):
    #     """Short summary.
    #     Updates the internal state from can and pushes to redis
    #     CAN Message is RC_Status , ID 0x110
    #     Signals :
    #         RC_statusXX -> 60 Bit for the relays XX is mutliplexer eg (01 or 00)
    #     """
    #     self.state = status

    def test_lb_contactor_card(self):
        used_ports = list(range(21))  # zero based
        self.check_card(9, used_ports)
