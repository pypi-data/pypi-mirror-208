
import time
from srsinst.uga import Keys

from srsgui import Task
from srsgui.task.inputs import InstrumentInput, ListInput, IntegerInput
from srsinst.uga import get_uga


class UGAModeControlTask(Task):
    """
    update
    """
    InstrumentName = 'uga to control'
    ModeName = 'mode control'
    UpdatePeriod = 'update period'
    LeakTestMass = 'mass for leak test'
    ModeList = [Keys.Start, Keys.Stop, Keys.Sleep, Keys.LeakTestOn, Keys.LeakTestOff,
                Keys.SystemBakeOn, Keys.SystemBakeOff]

    input_parameters = {
        InstrumentName: InstrumentInput(),
        ModeName: ListInput(ModeList),
        LeakTestMass: IntegerInput(4, ' AMU', 1, 100),
        UpdatePeriod: IntegerInput(2, ' s', 1, 60, 1)
    }

    def setup(self):
        self.logger = self.get_logger(__name__)
        self.params = self.get_all_input_parameters()

        self.uga = get_uga(self, self.params[self.InstrumentName])
        print(self.uga.status.id_string)
        while self.uga.status.error != 0:
            pass

        self.immediate_state = self.uga.mode.state
        self.final_state = self.immediate_state
        self.logger.info('Current mode before changing: {}'.format(self.immediate_state))

    def test(self):
        if self.params[self.ModeName] == Keys.Start:
            self.uga.mode.start()
            self.immediate_state = Keys.Start
            self.final_state = Keys.Ready

        elif self.params[self.ModeName] == Keys.Stop:
            self.uga.mode.stop()
            self.immediate_state = Keys.Stop
            self.final_state = Keys.Off

        elif self.params[self.ModeName] == Keys.Sleep:
            self.uga.mode.sleep()
            self.immediate_state = Keys.Sleep
            self.final_state = Keys.Idle

        elif self.params[self.ModeName] == Keys.LeakTestOn:
            if self.uga.mode.state != Keys.Ready:
                raise ValueError('Leak test mode is available only from READY state')
            self.uga.mode.leak_test_mass = self.params[self.LeakTestMass]
            self.uga.mode.leak_test = True
            self.immediate_state = Keys.Ready
            self.final_state = Keys.LeakTest

        elif self.params[self.ModeName] == Keys.LeakTestOff:
            if self.uga.mode.state != Keys.LeakTest:
                raise ValueError('Leak test mode is not on')

            self.uga.mode.leak_test = False
            self.immediate_state = Keys.LeakTest
            self.final_state = Keys.Ready

        elif self.params[self.ModeName] == Keys.SystemBakeOn:
            self.immediate_state = self.uga.mode.state
            self.uga.mode.bake = True
            self.final_state = Keys.SystemBake

        elif self.params[self.ModeName] == Keys.SystemBakeOff:
            if self.uga.mode.state != Keys.SystemBake:
                raise ValueError('SYSTEM BAKE is not on')
            self.uga.mode.bake = False
            self.immediate_state = Keys.Start
            self.final_state = Keys.Ready

        error_code = self.uga.status.error
        if error_code > 10:
            raise ValueError('Error "{}" when trying to change to  {}'
                             .format(self.uga.status.error_message[error_code], self.final_state))
        else:
            self.logger.info('UGA mode changing to {}'.format(self.final_state))

        self.display_device_info(device_name=self.params[self.InstrumentName], update=True)

        time.sleep(self.params[self.UpdatePeriod])
        current_state = self.uga.mode.state
        while current_state in [self.immediate_state, self.final_state]:
            if not self.is_running():
                break
            self.display_device_info(device_name=self.params[self.InstrumentName], update=True)
            current_state = self.uga.mode.state
            if current_state == self.final_state:
                self.logger.info('Mode successfully changed to {}'.format(self.final_state))
                break
            time.sleep(self.params[self.UpdatePeriod])

        self.display_device_info(device_name=self.params[self.InstrumentName], update=True)
        self.set_task_passed(True)

    def cleanup(self):
        pass
