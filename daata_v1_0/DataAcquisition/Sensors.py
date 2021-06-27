from abc import ABCMeta, abstractmethod
import logging
import math

logger = logging.getLogger("DataAcquisition")


class Sensor(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        from DataAcquisition import is_data_collecting
        self.is_data_collecting = is_data_collecting
        self.values = list()
        self.name = kwargs.get('name')
        self.object = kwargs.get('object')
        self.most_recent_index = 0
        self.current_value = None
        self.display_name = kwargs.get('display_name')
        self.unit = kwargs.get('unit')
        self.unit_short = kwargs.get('unit_short')
        self.is_plottable = kwargs.get('is_plottable', True)
        self.is_external = kwargs.get('is_external', True)
        self.is_derived = False
        self.is_connected = False
        self.is_float = kwargs.get('is_float')

    def add_value(self, value):
        try:
            self.current_value = value
            if self.is_data_collecting.is_set():
                self.values.append(value)
                self.most_recent_index = len(self.values) - 1
        except Exception as e:
            logger.error(e)

    def get_value(self, index):
        try:
            return self.values[index]
        except IndexError:
            logger.error("Index: {} out of range, use get_most_recent_index to ensure that the index exists".format(index))
            return None

    def get_values(self, index, num_values):
        try:
            try:
                assert index - num_values >= 0
                return self.values[index - num_values:index]
            except AssertionError:
                logger.debug("Tried to get more values than are contained, returning all values")
                return self.values[0:index]
        except IndexError:
            logger.error("Index: {} out of range, use get_most_recent_index to ensure that the index exists".format(index))
            return None

    def reset(self):
        try:
            logger.debug("Resetting the sensor {}".format(self.display_name))
            self.values = list()
            self.most_recent_index = 0
        except Exception as e:
            logger.error(e)


class Generic(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Flag(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_plottable = False


class Command(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_plottable = False


class Time(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_plottable = False


class Speed(Sensor):
    def __init__(self, pulses_per_revolution, **kwargs):
        super().__init__(**kwargs)
        self.ppr = pulses_per_revolution
        self.unit = kwargs.get('unit', "Revolutions Per Minute")
        self.unit_short = kwargs.get('unit_short', "RPM")


class Position(Sensor):
    def __init__(self, pulses_per_revolution, **kwargs):
        super().__init__(**kwargs)
        self.ppr = pulses_per_revolution
        self.unit = kwargs.get('unit', "Ticks")
        self.unit_short = kwargs.get('unit_short', "ticks")


class Pressure(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = kwargs.get('unit', "Pounds Per Square Inch")
        self.unit_short = kwargs.get('unit_short', "PSI")


class Force(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = kwargs.get('unit', "Pounds")
        self.unit_short = kwargs.get('unit_short', "lbs")


class LDS(Sensor):
    def __init__(self, stroke_length, **kwargs):
        super().__init__(**kwargs)
        self.stroke_length = stroke_length
        self.unit = kwargs.get('unit', "Millimeters")
        self.unit_short = kwargs.get('unit_short', "mm")


class Acceleration(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = kwargs.get('unit', "Meters per Second Squared")
        self.unit_short = kwargs.get('unit_short', "m/s^2")


class Gyro(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = kwargs.get('unit', "Degrees per Second")
        self.unit_short = kwargs.get('unit_short', "°/s")


class Temperature(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = kwargs.get('unit', "Degrees Farenheit")
        self.unit_short = kwargs.get('unit_short', "°F")
