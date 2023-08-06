
from srsgui import Component, Instrument

from srsgui import Command, GetCommand,\
                   BoolCommand, BoolGetCommand,\
                   IntCommand, IntGetCommand, IntSetCommand,\
                   FloatCommand, FloatSetCommand, FloatGetCommand, \
                   DictCommand, DictGetCommand

from srsgui import IndexCommand, IndexGetCommand, \
                   IntIndexCommand, IntIndexGetCommand, \
                   BoolIndexCommand, BoolIndexGetCommand,\
                   FloatIndexCommand, FloatIndexGetCommand
from srsinst.rga import RGA100
from .keys import Keys


class Mode(Component):
    ModeDict = {
        Keys.Off:         1,
        Keys.Start:       3,
        Keys.Stop:        4,
        Keys.Ready:       6,
        Keys.Sleep:       7,
        Keys.Idle:        8,
        Keys.LeakTest:   10,
        Keys.SystemBake: 12,
        Keys.Manual:     13
    }

    StateDict = {
        Keys.Off: 0,
        Keys.On: 1,
        Keys.Idle: 2,
        Keys.TurningOn3: 3,
        Keys.TurningOn4: 4,
        Keys.TurningOn5: 5,
        Keys.TurningOff6: 6,
        Keys.TurningOff7: 7,
        Keys.TurningIdle8: 8,
        Keys.TurningIdle9: 9,
        Keys.TurningIdle10: 10,
        Keys.Error: 12,
    }

    OffOnDict = {
        Keys.Off: 0,
        Keys.On:  1,
    }

    OffOnIdleDict = {
        Keys.Off:  0,
        Keys.On:   1,
        Keys.Idle: 2,
    }

    state = DictGetCommand('ZMOD', ModeDict)
    bake = BoolCommand('ZMBK')

    leak_test = BoolCommand('ZMLT')
    leak_test_mass = IntCommand('ZPLM', 'AMU')

    def start(self):
        self.comm.send('ZMST')

    def stop(self):
        self.comm.send('ZMSP')
        
    def sleep(self):
        self.comm.send('ZMSL')

    allow_run_button = [start, stop, sleep]


class BypassPump(Component):
    state = DictCommand('ZCBP', Mode.OffOnDict, Mode.StateDict)
    on_power = IntCommand('ZPBO', '%')

    def get_pressure(self):
        return self._parent.pressure.values[Keys.Bypass] * 1e-6

    
class RoughingPump(Component):
    state = DictCommand('ZCRP', Mode.OffOnIdleDict, Mode.StateDict)
    on_power = IntCommand('ZPRO', '%')
    idle_power = IntCommand('ZPRI', '%')

    def get_pressure(self):
        return self._parent.pressure.values[Keys.Roughting] * 1e-6

    
class TurboPump(Component):
    state = DictCommand('ZCTP', Mode.OffOnIdleDict, Mode.StateDict)
    speed = IntGetCommand('ZQHZ', 'Hz')
    current = FloatGetCommand('ZQCU', 'mA')
    temperature = IntGetCommand('ZQTT', '°C')

    def get_pressure(self):
        if self._parent.ig.state == Keys.On:
            return self._parent.pressure.values[Keys.Chamber] * 1e-12
        else:
            return 0.0


class BypassValve(Component):
    state = DictCommand('ZCBV', Mode.OffOnDict, Mode.StateDict)


class SampleValve(Component):
    state = DictCommand('ZCSV', Mode.OffOnDict, Mode.StateDict)
    auto = BoolCommand('ZPAS')


class VentValve(Component):
    state = DictCommand('ZCVV', Mode.OffOnDict, Mode.StateDict)
    auto = BoolCommand('ZPAV')


class RGA(RGA100):
    state = DictCommand('ZCRG', Mode.OffOnDict, Mode.StateDict)

    def __init__(self, parent):
        super().__init__()

        self._parent = parent
        self._parent._children.append(self)
        self._add_parent_to_index_commands()
        self.comm = parent.comm
        self.update_components()

        if self.comm.is_connected():
            if self.state == Keys.On:
                self.check_id()
   

class IonGauge(Component):
    """
    IonGauge component has two commands and one method:

    The state command turn on and off the ion gauge.
    The ion gauge can be turned on, only when the turbo pump is on or idle.

    The ion gauge has two filaments and if one is broken, you can select the other one.

    The method get_pressure() return the ion gauge pressure reading in Torr.
    """
    StateDict = {
        Keys.Off: 0,
        Keys.On: 1,
        Keys.Degas: 2
    }
    FilamentDict = {
        Keys.Filament1: 0,
        Keys.Filament2: 1
    }

    state = DictCommand('ZCIG', StateDict, Mode.StateDict)
    filament = DictCommand('ZPFL', FilamentDict)
    
    def get_pressure(self):
        """ Get the IG pressure in Torr"""
        return self._parent.pressure.values[Keys.IG] * 1e-12

    
class Heaters(Component):
    ModeDict = {
        Keys.Off: 0,
        Keys.BakeOn: 1,
        Keys.SampleOn: 2
    }
    HeaterDict = {
        Keys.Elbow: 0,
        Keys.Chamber: 1,
        Keys.SampleLine: 2,
        Keys.Capillary: 3
    }
    BakeHeaterDict = {
        Keys.Elbow: 0,
        Keys.Chamber: 1,
    }

    state = DictCommand('ZCHT', ModeDict, Mode.StateDict)
    bake_time = IntCommand('ZPBT', 'hr.')
    bake_time_remained = IntGetCommand('ZQBR', 'min.')
    bake_temperature = IntIndexCommand('ZPTB', 1, 0, BakeHeaterDict, '°C')
    sample_temperature = IntIndexCommand('ZPTH', 3, 0, HeaterDict, '°C')


class Temperature(Component):
    """
    Temperature component contains temperature measurements from 5 sensors.
    If the temperature calue us 255, the sensor is not working properly.
    """
    turbo_pump = IntGetCommand('ZQTT', '°C')
    elbow = IntGetCommand('ZQTA', '°C')
    chamber = IntGetCommand('ZQTB', '°C')
    sample_inlet = IntGetCommand('ZQTC', '°C')
    capillary = IntGetCommand('ZQTD', '°C')


class MultipleInlet(Component):
    channel = IntCommand('ZCMI')


class Pressure(Component):
    """
    Pressure component has two commands:

         Values are pressure measured with gauges:

            Pressure from Pirani and CM gauges are in the unit of uTorr (1e-6 Torr).
            pressure from IG is in the unit of pTorr (1e-12 Torr) regardless of the display unit

         Display_unit is to select the pressure unit for the front panel display.

            Reply from values command always in the unit of Torr.
    """
    GaugeDict = {
        Keys.Pirani: 0,
        Keys.Roughting: 0,
        Keys.CM: 2,
        Keys.Bypass: 2,
        Keys.IG: 3,
        Keys.Chamber: 3
    }

    UnitDict = {
        Keys.Torr: 0,
        Keys.Pascal: 1,
        Keys.MilliBar: 2,
        Keys.Bar: 3
    }
    values = IntIndexGetCommand('ZQAD', 3, 0, GaugeDict)
    display_unit = DictCommand('ZPPU', UnitDict)



class Ethernet(Component):
    mac_address = GetCommand('ZQMC')
    ip_address = Command('ZPIP')
    gateway = Command('ZPGW')
    subnet_mask = Command('ZPSM')
    login = Command('ZPNM')
    password = Command('ZPPW')
    full_duplex = BoolCommand('ZPDU')
    speed = IntCommand('ZPSP')
    timeout = IntCommand('ZPTO', 's')
    """A new timeout requires a power cycle to be effective."""
    exclude_capture = [login, password]


class Status(Component):
    StateBitDict = {
        15: ('Error', 'Occured', 'None'),
        14: (None, 'Power', 'On', 'Off'),  # always on when communicating
        13: ('Auto Mode', 'On', 'Off'),
        12: (None, None, None),
        11: ('Bake Mode', 'On', 'Off'),
        10: ('Heaters', 'On', 'Off'),
        9:  ('Vent Valve', 'Open', 'Closed'),
        8:  ('Ion Gauge', 'On', 'Off'),
        7:  ('RGA', 'On', 'Off'),
        6:  ('Sample Valve', 'Open', 'Closed'),
        5:  ('Bypass Valve', 'Open', 'Closed'),
        4:  ('TP Idle', 'On', 'Off'),
        3:  ('Turbo Pump', 'On', 'Off'),
        2:  ('RP Idle', 'On', 'Off'),
        1:  ('Roughing Pump', 'On', 'Off'),
        0:  ('Bypass Pump', 'On', 'Off')
    }

    pressure_interlock = BoolCommand('ZCPC')
    speaker_volume = IntCommand('ZCVL')
    
    id_string = GetCommand('ZQID')
    firmware_version = GetCommand('ZQFV')
    serial_number = GetCommand('ZQSN')
    baud_rate = IntCommand('ZPBA')

    states = IntGetCommand('ZBST')
    changed = IntGetCommand('ZBCT')
    changing = IntGetCommand('ZBTT')
    error = DictGetCommand('ZERR', Keys.ErrorMessageDict)
    error_message = IndexGetCommand('ZEDS', index_max=126)

    exclude_capture = [error_message]

    def get_status_text(self):
        out_buffer = ''
        error_buffer = 'Errors: '
        item_line_format = '{}: {} \n'
        
        states = self.states
        changed = self.changed
        changing = self.changing        

        out_buffer += item_line_format.format('Mode', self._parent.mode.state)
        
        for ind in Status.StateBitDict:
            item_name = Status.StateBitDict[ind][0]
            on_tag = Status.StateBitDict[ind][1]
            off_tag = Status.StateBitDict[ind][2]
            if item_name in (None, 'TP Idle', 'RP Idle'):
                continue

            mask = 1 << ind                
            if item_name == 'Error':
                if not states & mask:
                    error_buffer += off_tag
                    continue

                while True:
                    error = self.error
                    if error == Keys.OK:
                        break
                    error_buffer += '{}\n'.format(error)
                continue

            if item_name in ('Turbo Pump', 'Roughing Pump'):
                idle_mask = mask << 1
                if changing & idle_mask:                
                    text = item_line_format.format(item_name, 'Changing')
                elif states & idle_mask:
                    text = item_line_format.format(item_name, 'Idle')
                elif changing & mask:
                    text = item_line_format.format(item_name, 'Changing')
                elif states & mask:
                    text = item_line_format.format(item_name, on_tag)
                else:
                    text = item_line_format.format(item_name, off_tag)
                out_buffer += text
                continue
                
            if changing & mask:
                text = item_line_format.format(item_name, 'Changing')
            elif states & mask:
                text = item_line_format.format(item_name, on_tag)
            else:
                text = item_line_format.format(item_name, off_tag)
            out_buffer += text
            
        out_buffer += error_buffer   
        return out_buffer
