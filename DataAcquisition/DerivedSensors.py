from abc import ABCMeta, abstractmethod, abstractproperty
import logging
import math

logger = logging.getLogger("DataAcquisition")


class DerivedSensor(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.display_name = kwargs.get('display_name')
        self.unit = kwargs.get('unit')
        self.unit_short = kwargs.get('unit_short')
        self.is_plottable = kwargs.get('is_plottable', True)
        self.is_external = kwargs.get('is_external',
                                      True)  # If it relies on external sensors consider it external
        self.is_derived = True

    @abstractmethod
    def get_value(self, index):
        raise NotImplementedError

    @abstractmethod
    def get_values(self, index, num_values):
        raise NotImplementedError

    @abstractproperty
    def is_connected(self):
        raise NotImplementedError

    @abstractproperty
    def current_value(self):
        raise NotImplementedError


"""
This dictionary stores all the information needed for creating derived sensor objects

To add a sensor, add an element to the derived_sensors dictionary with the 
keyword being the name of that sensor. This should match the id that is
found in the SensorId.h file in the comms utility (DAQ>Libraries>Sensor).
Then add all the required parameters for that sensor along with any 
additional optional parameters.

Required parameters:
    - object
    - sensors (must be a list, even if only one sensor needed)

Optional parameters:
    - display_name   (defaults to None)
    - unit           (defaults to None)
    - unit_short     (defaults to None)
    - is_plottable   (defaults to True)

Current classes:
    - dashboard
    - aux_daq
    - differential
    - engine_dyno
    - shock_dyno


"""
derived_sensors = {
    'dyno_torque_ftlbs': {
        'object': 'Torque',
        'sensors': ['force_enginedyno_lbs'],
        'display_name': "Dyno Torque",
        'transfer_function': 8 / 12  # Since the lever arm is 8" away
    },
    'power_engine_horsepower': {
        'object': 'MechanicalPower',
        'sensors': ['dyno_torque_ftlbs', 'dyno_engine_speed'],
        'display_name': "Engine Output Power"  # transfer function is 1/5252
    },
    'ratio_dyno_cvt': {
        'object': 'Ratio',
        'sensors': ['dyno_engine_speed', 'dyno_secondary_speed'],
        'display_name': "Dyno CVT Ratio"
        # dyno_engine_speed / dyno_secondary_speed
    }
}


class WheelSpeed(DerivedSensor):
    def __init__(self, secondary_speed, **kwargs):
        super().__init__(**kwargs)
        self.display_name = "Wheel Speed"
        self.unit = 'Revolutions Per Minute'
        self.unit_short = 'RPM'
        self.secondary_speed = secondary_speed
        self.gearbox_ratio = 0  # TODO: Need to get the gearbox ratio

    def get_value(self, index):
        return self.secondary_speed.get_value(index) * self.gearbox_ratio

    def get_values(self, index, num_values):
        return [value * self.gearbox_ratio for value in
                self.secondary_speed.get_values(index, num_values)]

    @property
    def is_connected(self):
        return self.secondary_speed.is_connected

    @property
    def current_value(self):
        return self.secondary_speed.current_value * self.gearbox_ratio


class CarSpeed(DerivedSensor):
    def __init__(self, secondary_speed, **kwargs):
        super().__init__(**kwargs)
        self.display_name = "Car Speed"
        self.unit = 'Miles Per Hour'
        self.unit_short = 'MPH'
        self.secondary_speed = secondary_speed
        self.transfer_function = 0  # TODO: Need to get the transfer function

    def get_value(self, index):
        return self.secondary_speed.get_value(index) * self.transfer_function

    def get_values(self, index, num_values):
        return [value * self.transfer_function for value in
                self.secondary_speed.get_values(index, num_values)]

    @property
    def is_connected(self):
        return self.secondary_speed.is_connected

    @property
    def current_value(self):
        return self.secondary_speed.current_value * self.transfer_function


class Torque(DerivedSensor):
    def __init__(self, force_lbs, **kwargs):
        super().__init__(**kwargs)
        self.display_name = kwargs.get('display_name', "Torque")
        self.unit = kwargs.get('unit', 'Foot-Pounds')
        self.unit_short = kwargs.get('unit', 'ft-lbs')
        self.force_lbs = force_lbs
        self.transfer_function = kwargs.get('transfer_function', 1)

    def get_value(self, index):
        return self.force_lbs.get_value(index) * self.transfer_function

    def get_values(self, index, num_values):
        return [value * self.transfer_function for value in
                self.force_lbs.get_values(index, num_values)]

    @property
    def is_connected(self):
        return self.force_lbs.is_connected

    @property
    def current_value(self):
        return self.force_lbs.current_value * self.transfer_function


class MechanicalPower(DerivedSensor):
    def __init__(self, torque_ftlbs, speed_rpm, **kwargs):
        super().__init__(**kwargs)
        self.display_name = kwargs.get('display_name', "Power")
        self.unit = kwargs.get('unit', 'Horsepower')
        self.unit_short = kwargs.get('unit', 'HP')
        self.torque_ftlbs = torque_ftlbs
        self.speed_rpm = speed_rpm
        self.transfer_function = kwargs.get('transfer_function',
                                            1 / 5252)  # HP = RPM * Torque / 5252

    def get_value(self, index):
        return self.torque_ftlbs.get_value(index) * self.speed_rpm.get_value(
            index) * self.transfer_function

    def get_values(self, index, num_values):
        return [force * rpm * self.transfer_function for force, rpm in
                zip(self.torque_ftlbs.get_values(index, num_values),
                    self.speed_rpm.get_values(index, num_values))]

    @property
    def is_connected(self):
        return self.torque_ftlbs.is_connected and self.speed_rpm.is_connected

    @property
    def current_value(self):
        return self.torque_ftlbs.current_value * self.speed_rpm.current_value * self.transfer_function


class Ratio(DerivedSensor):
    DEFAULT_INF_VALUE = 10e6

    def __init__(self, input_speed_rpm, output_speed_rpm, **kwargs):
        super().__init__(**kwargs)
        self.display_name = kwargs.get('display_name', "Ratio")
        self.unit = kwargs.get('unit', None)
        self.unit_short = kwargs.get('unit', None)
        self.input_speed_rpm = input_speed_rpm
        self.output_speed_rpm = output_speed_rpm
        self.transfer_function = kwargs.get('transfer_function', 1)

    def get_value(self, index):
        if self.output_speed_rpm.get_value(index) == 0:
            return self.DEFAULT_INF_VALUE
        return self.input_speed_rpm.get_value(
            index) / self.output_speed_rpm.get_value(
            index) * self.transfer_function

    def get_values(self, index, num_values):
        values = list()
        for input_speed, output_speed in zip(
                self.input_speed_rpm.get_values(index, num_values),
                self.output_speed_rpm.get_values(index, num_values)):
            if output_speed == 0:
                values.append(10e6)
            else:
                values.append(
                    input_speed / output_speed * self.transfer_function)
        return values

    @property
    def is_connected(self):
        return self.input_speed_rpm.is_connected and self.output_speed_rpm.is_connected

    @property
    def current_value(self):
        if self.output_speed_rpm.current_value == 0:
            return 10e6
        return self.input_speed_rpm.current_value / self.output_speed_rpm.current_value * self.transfer_function
