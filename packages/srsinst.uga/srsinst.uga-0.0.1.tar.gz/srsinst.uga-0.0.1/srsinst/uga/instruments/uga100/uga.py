
from srsgui.inst.component import Component
from srsgui.inst.instrument import Instrument, SerialInterface, TcpipInterface
from srsgui.inst.exceptions import InstIdError

from srsgui.task.inputs import FindListInput, IntegerListInput, Ip4Input, StringInput, PasswordInput

from .components import BypassPump, RoughingPump, TurboPump, \
                        BypassValve, SampleValve, VentValve, \
                        RGA, IonGauge,  MultipleInlet, \
                        Pressure, Heaters, Temperature, \
                        Ethernet, Status, Mode
from .keys import Keys


class UGA100(Instrument):
    _IdString = 'SRS_UGA'
    _term_char = b'\r'

    available_interfaces = [
        [   SerialInterface,
            {
                'port': FindListInput(),
                'baud_rate': IntegerListInput([28800, 38400]),
                'hardware_flow_control': True
            }
        ],
        [   TcpipInterface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
                'user_id': StringInput('srsuga'),
                'password': PasswordInput('srsuga'),
                'port': 818
            }
        ]
    ]

    def __init__(self, interface_type=None, *args):
        super().__init__(interface_type, *args)

        self.mode = Mode(self)
        self.bp = BypassPump(self)
        self.rp = RoughingPump(self)
        self.tp = TurboPump(self)
        self.bv = BypassValve(self)
        self.sv = SampleValve(self)
        self.vv = VentValve(self)
        self.rga = RGA(self)
        self.ig = IonGauge(self)
        self.mi = MultipleInlet(self)
        self.ht = Heaters(self)

        self.temperature = Temperature(self)
        self.pressure = Pressure(self)
        self.ethernet = Ethernet(self)
        self.status = Status(self)

    def check_id(self):
        if not self.is_connected():
            return None, None, None

        reply = self.query_text('ZQID?').strip()
        strings = reply.split(',')

        if len(strings) != 3:
            return None, None, None

        model_name = strings[0].strip()
        serial_number = strings[1].strip()[4:]
        firmware_version = strings[2].strip()[2:]

        if self._IdString not in reply:
            raise InstIdError("Invalid instrument: {} not in {}"
                              .format(self._IdString, reply))
        if self.rga.state == Keys.On:
            self.rga.check_id()  # configure RGA

        if 'UGA_HT' in model_name:
            if hasattr(self, 'bv'):
                del self.bv
            if hasattr(self, 'sv'):
                del self.sv
            if hasattr(self, 'mi'):
                del self.mi
            if not hasattr(self, 'bp'):
                self.bp = BypassPump(self)
        elif 'UGA_LT' in model_name:
            if not hasattr(self, 'bv'):
                self.bv = BypassValve(self)
            if not hasattr(self, 'sv'):
                self.sv = SampleValve(self)
            if not hasattr(self, 'mi'):
                self.mi = MultipleInlet(self)
            if hasattr(self, 'bp'):
                del self.bp
        elif 'UGA_PM' in model_name:
            if hasattr(self, 'bv'):
                del self.bv
            if not hasattr(self, 'sv'):
                self.sv = SampleValve(self)
            if not hasattr(self, 'mi'):
                self.mi = MultipleInlet(self)
            if hasattr(self, 'bp'):
                del self.bp
        elif 'UGA' in model_name:
            if not hasattr(self, 'bv'):
                self.bv = BypassValve(self)
            if not hasattr(self, 'sv'):
                self.sv = SampleValve(self)
            if not hasattr(self, 'mi'):
                self.mi = MultipleInlet(self)
            if not hasattr(self, 'bp'):
                self.bp = BypassPump(self)

        self._id_string = reply
        self._model_name = model_name
        self._serial_number = serial_number
        self._firmware_version = firmware_version
        return self._model_name, self._serial_number, self._firmware_version
        
    def get_status(self):
        return self.status.get_status_text()

    def reset(self):
        self.comm.send('ZRST')

    def handle_command(self, cmd_string: str):
        cmd = cmd_string.upper()
        reply = ''
        if '?' in cmd or cmd.startswith("FL") or cmd.startswith("HV") or \
                cmd.startswith("VF") or cmd.startswith("EE") or \
                cmd.startswith("IE") or cmd.startswith("IN"):
            reply = self.query_text(cmd).strip()
        elif cmd.startswith("MR"):
            # self.send(cmd)
            try:
                mass = int(cmd[2:].strip())
                intensity = self.rga.scan.get_single_mass_scan(mass)  # read_long()
                reply = str(intensity)
            except:
                pass
        elif cmd.startswith("SC") and len(cmd) < 10:
            self.rga.scan.get_analog_scan()
            reply = "Scan Completed"
        elif cmd.startswith("HS"):
            self.rga.scan.get_histogram_scan()
            reply = "Scan Completed"
        else:
            self.send(cmd)
        return reply


if __name__ == '__main__':
    uga = UGA100('tcpip', '172.25.128.13', 'srsuga', 'srsuga')
    print(uga.status.id_string)

