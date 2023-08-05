import logging

import can
import time
import cantools
from cantools.database.can.signal import NamedSignalValue


class DACController(object):

    def __init__(self):
        self.can_db = cantools.database.Database()
        self.bus = None
        # Setup DAC states 5 Dacs with 4 channels initially set to 0.5V
        self.dacs = {0: [0.5, 0.5, 0.5, 0.5],
                     1: [0.5, 0.5, 0.5, 0.5],
                     2: [0.5, 0.5, 0.5, 0.5],
                     3: [0.5, 0.5, 0.5, 0.5],
                     4: [0.5, 0.5, 0.5, 0.5]}
        return

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def set(self, channel, value):
        """Short summary.
        Sets a dac voltage to a specific number
        Parameters
        ----------
        channel : int
            channel number
        value : float
            voltage to be set
        """

        dac = (channel // 4)
        dac_ch = (channel % 4)
        self.dacs[dac][dac_ch] = float(value)
        self.update_dac(dac, dac_ch)

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

    def update_dac(self, dac_no, ch_no):
        """Short summary.
        Updates a Dac with the strored state

        Message ID is 0x22a-e
        Message Name is : DAC_CMB_Cntrl_0i
        Signal name is DAC_CMB_Cntrl_0y_0z_Voltage
        where y = 1-5 for 5 Dacs
        and z = 1-4 for 4 Channels per DAC
        """
        cmd = {}
        msg_name = f"DAC_CMB_Cntrl"
        # for ch_no in range (4):
        cmd["DAC_CMB_Cntrl_Channel"] = (dac_no) * 0x10 + ch_no  # set the multiplexor
        signal_name = f"DAC_CMB_Cntrl_{str(dac_no + 1).zfill(2)}_{str(ch_no + 1).zfill(2)}_Voltage"
        cmd[signal_name] = self.dacs[dac_no][ch_no]
        self.bus.send(f"{msg_name}", cmd)


class CMBFaultBoard:

    def __init__(self):
        """Short summary.
        Initialization for CMBFaultClass
        Returns
        -------
        type
            Description of returned object.

        """
        self.can_db = cantools.database.Database()
        self.bus = None
        self.id = id
        self.state = {}
        self.channels = 19  # amount of channels for the board -> is 19
        for cell in range(self.channels):
            self.state[f"cell{cell}"] = {"open_circuit": 0, "high_impedance": 0}
        self.state["supply_plus"] = {"open_circuit": 0}
        self.state["supply_minus"] = {"open_circuit": 0}
        self.state["communication1"] = {"open_circuit": 0}
        self.state["communication2"] = {"open_circuit": 0}

        return

    def set(self, channel, function, value):
        try:
            if channel in self.state:
                if function in self.state[channel]:
                    self.state[channel][function] = bool(int(value))
        except:
            print(f"Error in setting fault {function} for channel {channel} with value {value}")
        self.send_state_to_board()

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
        self.bus.send(message)

    def send_cmb_relay_can_message(self, cell, type, val):
        cmd = {f'RCCMBCntrl_CV{cell}_{type}': val}
        self.send_can_message("RCCMBCntrl", cmd)

    def send_state_to_board(self):
        data = {}
        for i in range(self.channels):
            # Set open circuit state
            data[f"RCCMBCntrl_CV{i}_OC"] = self.state[f"cell{i}"]["open_circuit"]
            # Set high impedance state
            data[f"RCCMBCntrl_CV{i}_HImp"] = self.state[f"cell{i}"]["high_impedance"]

        data["RCCMBCntrl_SupplyPlus"] = self.state["supply_plus"]["open_circuit"]
        data["RCCMBCntrl_SupplyMinus"] = self.state["supply_minus"]["open_circuit"]
        data["RCCMBCntrl_CommDaisyChain1"] = self.state["communication1"]["open_circuit"]
        data["RCCMBCntrl_CommDaisyChain2"] = self.state["communication2"]["open_circuit"]
        print(data)
        self.send_can_message(f"RCCMBCntrl", data)
        self.bus.send(self.state)

    def test_cell_fault_board(self):
        for cell in range(18):
            print(f"Testing Open Circuit on cell {cell}")
            self.send_cmb_relay_can_message(cell, "OC", 1)
            time.sleep(0.5)
            self.send_cmb_relay_can_message(cell, "OC", 0)
            time.sleep(0.1)

        for cell in range(18):
            print(f"Testing High Impedance on cell {cell}")
            self.send_cmb_relay_can_message(cell, "HImp", 1)
            time.sleep(0.5)
            self.send_cmb_relay_can_message(cell, "HImp", 0)
            time.sleep(0.1)
