import sys
from typing_extensions import final
import serial
from serial.serialutil import EIGHTBITS
from serial.tools import list_ports
import time
import logging
from datetime import datetime
import random
import math

from DataAcquisition.Data import Data
from DataAcquisition.SensorId import SensorId

logger = logging.getLogger("DataImport")


class DataImport:
    def __init__(self, data, lock, is_data_collecting, use_fake_inputs):
        self.data = data
        self.lock = lock
        self.use_fake_inputs = use_fake_inputs
        self.is_data_collecting = is_data_collecting
        self.start_time = datetime.now()

        # Connect to the Teensy
        self.connect_serial()

        self.end_code = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf0]
        self.current_sensors = []
        self.current_packet = []
        self.ack_code = 0
        self.packet_index = 0
        self.expected_size = 0

        self.is_receiving_data = False
        self.is_sending_data = False

        # Variables needed for fake data
        self.time_begin = datetime.now()
        self.prev_time = datetime.now()
        self.prev_engine_val = 1800
        self.prev_lds_val = 0
        self.prev_br_lds_val = 0
        self.prev_bl_lds_val = 0
        self.prev_fr_lds_val = 0

        self.temp_data = {}
        for sensor in data.get_sensors(is_external=True, is_derived=False):
            self.temp_data[sensor] = {'value': None, 'has_been_updated': False, 'is_used': False}

    def check_connected(self):
        return self.teensy_ser.is_open

    def update(self):
        """
        if self.use_fake_inputs:
            self.check_connected_fake()
        """
        try:
            assert self.teensy_found
            try:
                assert self.teensy_ser.is_open
                self.read_packet()
                self.send_packet()
            except AssertionError:
                logger.info("Serial port is not open, opening now")
                try:
                    self.teensy_ser.open()
                except Exception as e:
                    logger.error(e)
        except AssertionError:
            logger.debug("No compatible Teensy found")

    def connect_serial(self):
        # # Teensy USB serial microcontroller program id data to fill out:
        # vendor_id = "16C0"
        # product_id = "0483"
        # serial_number = "12345"
        #
        # for port in list(list_ports.comports()):
        #     if port[2] == "USB VID:PID=%s:%s SNR=%s"%(vendor_id, product_id, serial_number):
        #         return port[0]

        # Manually change the COM port below to the correct
        # port that the teensy appears on your device manager for now
        try:
            self.teensy_port = 'COM12'
            self.teensy_ser = serial.Serial(baudrate=115200, port=self.teensy_port, timeout=2,
                                            write_timeout=1)
            time.sleep(2)
            logger.info("Teensy found on port {}".format(self.teensy_ser.port))
            self.teensy_found = True
        except Exception as e:
            self.teensy_found = False
            logger.error(e)

    def read_packet(self):
        try:
            while self.teensy_ser.in_waiting != 0:  # if there are bytes waiting in input buffer
                self.current_packet.append(self.teensy_ser.read(1))  # read in a single byte
                packet_length = len(self.current_packet)
                if packet_length > 8:
                    # If end code is found then unpacketize and clear packet
                    end_code_match = True
                    for i in range(len(self.end_code)):
                        if int.from_bytes(self.current_packet[(packet_length - 8):(packet_length)][i], "little") != \
                                self.end_code[i]:
                            end_code_match = False
                    if end_code_match:
                        self.current_packet = self.current_packet[0:(packet_length - 8)]
                        self.unpacketize()
                        self.current_packet.clear()
        except Exception as e:
            logger.debug(e)

    def send_packet(self):
        try:
            self.teensy_ser.write(self.packetize())
        except Exception as e:
            logger.error(e)

    def packetize(self):
        ack_0 = b'\x00\xff\xff\xff\xff\xff\xff\xff\xf0'
        ack_1 = b'\x01\xff\xff\xff\xff\xff\xff\xff\xf0'
        ack_2 = b'\x02\xff\xff\xff\xff\xff\xff\xff\xf0'
        ack_3 = b'\x03\xff\xff\xff\xff\xff\xff\xff\xf0'

        if self.is_sending_data and self.is_receiving_data:
            return ack_3
        elif self.is_sending_data and not self.is_receiving_data:
            return ack_2
        elif not self.is_sending_data and self.is_receiving_data:
            return ack_1
        else:
            return ack_0

    def unpacketize(self):
        try:
            self.ack_code = int.from_bytes(self.current_packet[0],
                                           "little")  # Convert byte string to int for comparison
            self.current_packet.pop(0)  # Remove the ack code from the packet

            # if 0x02, then parse data but send settings
            # if 0x03, then parse data and send data
            if self.ack_code == 0x02 or self.ack_code == 0x03:
                logger.debug("Received data and will now parse")
                try:
                    assert len(self.current_packet) == self.expected_size
                    for sensor_id in self.current_sensors:
                        if isinstance(SensorId[sensor_id]["num_bytes"], list):
                            data_value = []
                            for sensor in range(len(SensorId[sensor_id]["num_bytes"])):
                                individual_data_value = b''
                                for i in range(SensorId[sensor_id]["num_bytes"][sensor]):
                                    individual_data_value += self.current_packet[0]
                                    self.current_packet.pop(0)
                                data_value.append(int.from_bytes(individual_data_value, "little"))
                        else:
                            data_value = b''
                            for i in range(SensorId[sensor_id]["num_bytes"]):
                                data_value += self.current_packet[0]
                                self.current_packet.pop(0)
                            data_value = int.from_bytes(data_value, "little")

                        print(data_value)
                        self.data.add_value(sensor_id, data_value)

                    time = (datetime.now() - self.start_time).total_seconds()
                    self.data.add_value(101, time)
                except AssertionError:
                    logger.warning("Packet size is different than expected")
                    self.is_receiving_data = False

            # if 0x00, then parse settings and send settings
            # if 0x01, then parse settings and send data
            elif self.ack_code == 0x00 or self.ack_code == 0x01:
                logger.info("Settings are being received")

                # Sets sensors from previous settings to disconnected
                for sensor_id in self.current_sensors:
                    self.data.set_disconnected(sensor_id)
                self.current_sensors.clear()
                self.expected_size = 0
                self.data.set_connected(101)

                try:
                    this_sensor_id = None
                    for i in range(0, len(self.current_packet), 3):
                        this_sensor_id = int.from_bytes(self.current_packet[i] + self.current_packet[i + 1], "little")
                        if type(SensorId[this_sensor_id]["num_bytes"]) == type(list()):
                            num_bytes = sum(SensorId[this_sensor_id]["num_bytes"])
                        else:
                            num_bytes = SensorId[this_sensor_id]["num_bytes"]
                        assert int.from_bytes(self.current_packet[i + 2], "little") == num_bytes

                        self.current_sensors.append(this_sensor_id)
                        self.data.set_connected(this_sensor_id)
                        self.expected_size += num_bytes

                        self.is_receiving_data = True
                    logger.info("Received settings of length: {}".format(self.expected_size))
                except AssertionError:
                    logger.error("The given number of bytes for " +
                                 "{} sensor did not match the expected size".format(SensorId[this_sensor_id]["name"]))
            else:
                logger.error("The ack code that was received was not a valid value")
        except Exception as e:
            logger.error(e)

    # def attach_output_sensor(self):

    def check_connected_fake(self):
        self.data.set_connected("time")
        self.start_time = datetime.now()
        if (datetime.now() - self.time_begin).total_seconds() > 0:
            self.data.is_connected = True
            self.data.set_connected("engine_rpm")
            self.data.set_connected("secondary_rpm")
            self.data.set_connected("fl_lds")
            self.data.set_connected("br_lds")
            self.data.set_connected("fr_lds")
            self.data.set_connected("bl_lds")

        if (datetime.now() - self.time_begin).total_seconds() > 6:
            self.data.set_disconnected("fl_lds")
            self.data.set_disconnected("br_lds")
            self.data.set_disconnected("fr_lds")
            self.data.set_disconnected("bl_lds")

    def read_data_fake(self):
        with self.lock:
            if not self.data.is_connected:
                self.check_connected_fake()
            else:
                if (datetime.now() - self.prev_time).total_seconds() * 1000 > 5:
                    time = (datetime.now() - self.start_time).total_seconds()

                    self.data.add_value("time", time)

                    self.prev_engine_val = max(1800, min(4000, self.prev_engine_val + 0.5 * math.sin(
                        time * 10) + random.randrange(-2, 2)))
                    self.data.add_value('engine_rpm', self.prev_engine_val)

                    # temp_t = time%8-4
                    temp_t = time % 6 - 4
                    self.prev_secondary_rpm_val = abs(2 * temp_t * math.exp(temp_t)
                                                      - math.exp(1.65 * temp_t))
                    self.data.add_value('secondary_rpm', self.prev_secondary_rpm_val)

                    self.prev_lds_val = 100 + 100 * math.sin(time / 20)
                    self.data.add_value('fl_lds', self.prev_lds_val)

                    self.prev_br_lds_val = max(1800, min(4000, self.prev_engine_val + 0.5 * math.sin(
                        time * 10) + random.randrange(-2, 2)))
                    self.data.add_value('br_lds', self.prev_br_lds_val)

                    self.prev_bl_lds_val = 100 + 100 * math.sin(time * 2) \
                                           + 100 * math.sin(time * 3.2) \
                                           + 100 * math.sin(time * 5.5) \
                                           + 100 * math.sin(time * 11.4)
                    self.data.add_value('bl_lds', self.prev_bl_lds_val)

                    self.prev_fr_lds_val = math.e ** (3 * math.sin(5 * time)) * abs(math.cos(5 * time)) + \
                                           50 * math.cos(time) \
                                           + 25 * math.cos(1 / 4 * time - math.pi / 6) \
                                           + 20 * math.cos(1 / 25 * time - math.pi / 3) \
                                           + 100 + random.randrange(-2, 2)
                    self.data.add_value('fr_lds', self.prev_fr_lds_val)
