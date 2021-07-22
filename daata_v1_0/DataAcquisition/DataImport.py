import sys
from typing_extensions import final
import serial
from serial.serialutil import EIGHTBITS
from serial.tools import list_ports
from serial.serialutil import SerialException
from DataAcquisition.ComPortUtil import ListPortsDialog
import time
import logging
from datetime import datetime
import random
import math
import struct

from DataAcquisition.Data import Data
from DataAcquisition.SensorId import SensorId

logger = logging.getLogger("DataImport")

# TODO - We never set self.is_sending_data... this needs to be fixed

class DataImport:
    def __init__(self, data, lock, is_data_collecting, use_fake_inputs):
        self.data = data
        self.lock = lock
        self.use_fake_inputs = use_fake_inputs
        self.is_data_collecting = is_data_collecting
        self.start_time = datetime.now()

        # Connect to the Teensy
        self.connect_serial()

        # Variables that are used for reading/parsing incoming packets
        self.end_code = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf0]
        self.current_sensors = []
        self.current_packet = []
        self.ack_code = 0
        self.packet_index = 0
        self.expected_size = 0

        # Variables that set the ack for sending packets
        self.is_receiving_data = False
        self.is_sending_data = False
        self.sending_period = 0.2  # in seconds
        self.last_send_time = datetime.now()

        # Variables that are used for creating/sending packets
        self.output_sensors = list()
        self.internal_sensors = list()

        # Variables needed for fake data
        self.time_begin = datetime.now()
        self.prev_time = datetime.now()
        self.prev_engine_val = 1800
        self.prev_lds_val = 0
        self.prev_br_lds_val = 0
        self.prev_bl_lds_val = 0
        self.prev_fr_lds_val = 0

    def check_connected(self):
        if self.teensy_ser.is_open:
            self.data.is_connected = True
            return True
        else:
            self.data.is_connected = False
            return False

    def update(self):
        """
        This is the main function that gets called in the data collection thread that manages the connection
        to the serial port and will read packets and parse them and send any necessary packets.

        :return: None
        """
        if self.use_fake_inputs:
            self.check_connected_fake()
            self.read_data_fake()
        else:
            try:
                assert self.teensy_found
                try:
                    assert self.check_connected()
                    self.read_packet()
                    if (datetime.now() - self.last_send_time).total_seconds() > self.sending_period:
                        self.send_packet()
                        self.last_send_time = datetime.now()
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
            #form = ListPortsDialog()
            #form.show()
            #self.teensy_port = form.chosen_port
            self.teensy_port = 'COM4'
            self.teensy_ser = serial.Serial(baudrate=115200, port=self.teensy_port, timeout=2,
                                            write_timeout=1)
            time.sleep(2)
            logger.info("Teensy found on port {}".format(self.teensy_ser.port))
            self.teensy_found = True
        except Exception as e:
            self.teensy_found = False
            logger.error(e)

    def read_packet(self):
        """
        read_packet manages all incoming data on the Serial port and detects when a full packet has been received
        so that it can be parsed.

        :return: None
        """
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
        """
        unpacketize is the function that is called when a full packet has been received. This function will parse
        the packet and will either store the received settings or data based on what type of packet was received.

        :return: None
        """
        try:
            self.ack_code = int.from_bytes(self.current_packet[0],
                                           "little")  # Convert byte string to int for comparison
            #print(self.current_packet)
            print_data = list()
            for data_val in self.current_packet:
                print_data.append(hex(int.from_bytes(data_val, "little")))
            print(print_data)
            self.current_packet.pop(0)  # Remove the ack code from the packet

            # if 0x02, then parse data but send settings
            # if 0x03, then parse data and send data
            if self.ack_code == 0x02 or self.ack_code == 0x03:
                with self.lock:
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
                                    # Branch if the value is a float by checking SensorID
                                    try:
                                        if SensorId[sensor_id][sensor]["is_float"]:
                                            data_value.append(struct.unpack('f', individual_data_value)[0])
                                        else:
                                            data_value.append(int.from_bytes(individual_data_value, "little"))
                                    except KeyError:
                                        data_value.append(int.from_bytes(individual_data_value, "little"))
                            else:
                                data_value = b''
                                for i in range(SensorId[sensor_id]["num_bytes"]):
                                    data_value += self.current_packet[0]
                                    self.current_packet.pop(0)
                                # Branch if the value is a float by checking SensorID
                                try:
                                    if SensorId[sensor_id]["is_float"]:
                                        data_value = struct.unpack('f', data_value)[0]
                                    else:
                                        data_value = int.from_bytes(data_value, "little")
                                except KeyError:
                                    data_value = int.from_bytes(data_value, "little")

                            #print(data_value)
                            self.data.add_value(sensor_id, data_value)

                        time = (datetime.now() - self.start_time).total_seconds()
                        self.data.add_value(101, time)
                    except AssertionError:
                        logger.warning("Packet size is different than expected")
                        self.is_receiving_data = False
                    except Exception as e:
                        logger.error(e)

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

    def attach_output_sensor(self, sensor_id):
        with self.lock:
            try:
                assert sensor_id in SensorId.keys()
                if sensor_id in self.output_sensors:
                    logger.warning("Attempted attaching output sensor with id {}. This sensor is already attached.".format(sensor_id))
                elif sensor_id in self.internal_sensors:
                    logger.warning("Sensor with id {} was attached as an internal sensor. Moved to output sensor.".format(sensor_id))
                    self.internal_sensors.remove(sensor_id)
                    self.output_sensors.append(sensor_id)
                else:
                    self.output_sensors.append(sensor_id)
                self.data.set_connected(sensor_id)
            except AssertionError:
                logger.error("Attempted attaching ouptput sensor with id {}. This sensor does not exist".format(sensor_id))
            logger.debug("Successfully attached output sensor with id {}".format(sensor_id))

    def detach_output_sensor(self, sensor_id):
        with self.lock:
            try:
                assert sensor_id in SensorId.keys()
                self.data.set_disconnected(sensor_id)
                if sensor_id in self.output_sensors:
                    self.output_sensors.remove(sensor_id)
                else:
                    logger.warning("Attempted detaching output sensor with id {}. This sensor wasn't attached.".format(sensor_id))
            except AssertionError:
                logger.error("Attempted detaching output sensor with id {}. This sensor does not exist".format(sensor_id))
            logger.debug("Successfully detached output sensor with id {}".format(sensor_id))

    def attach_internal_sensor(self, sensor_id):
        with self.lock:
            try:
                assert sensor_id in SensorId.keys()
                if sensor_id in self.internal_sensors:
                    logger.warning("Attempted attaching internal sensor with id {}. This sensor is already attached.".format(sensor_id))
                elif sensor_id in self.output_sensors:
                    logger.warning("Attempted attaching internal sensor with id {}. Already attached as output sensor.".format(sensor_id))
                else:
                    self.output_sensors.append(sensor_id)
                self.data.set_connected(sensor_id)
            except AssertionError:
                logger.error("Attempted attaching sensor with id {}. This sensor does not exist".format(sensor_id))
            logger.debug("Successfully attached internal sensor with id {}".format(sensor_id))

    def detach_internal_sensor(self, sensor_id):
        with self.lock:
            try:
                assert sensor_id in SensorId.keys()
                self.data.set_disconnected(sensor_id)
                if sensor_id in self.internal_sensors:
                    self.internal_sensors.remove(sensor_id)
                else:
                    logger.warning("Attempted detaching internal sensor with id {}. This sensor wasn't attached.".format(sensor_id))
            except AssertionError:
                logger.error("Attempted detaching internal sensor with id {}. This sensor does not exist".format(sensor_id))
            logger.debug("Successfully detached internal sensor with id {}".format(sensor_id))

    def check_connected_fake(self):
        if self.is_data_collecting and not self.data.is_connected:
            self.data.set_connected(101)  # Time ID
            self.start_time = datetime.now()
            if (datetime.now() - self.time_begin).total_seconds() > 0:
                self.data.is_connected = True
                self.data.set_connected(90)
                self.data.set_connected(91)
                self.data.set_connected(92)
                self.data.set_connected(93)
                self.data.set_connected(94)
                self.data.set_connected(95)
        elif not self.is_data_collecting:
            self.data.is_connected = False

    def read_data_fake(self):
        with self.lock:
            if not self.data.is_connected:
                self.check_connected_fake()
            else:
                if (datetime.now() - self.prev_time).total_seconds() * 1000 > 5:
                    time = (datetime.now() - self.start_time).total_seconds()

                    self.data.add_value(101, time)

                    self.prev_engine_val = max(1800, min(4000, self.prev_engine_val + 0.5 * math.sin(
                        time * 10) + random.randrange(-2, 2)))
                    self.data.add_value(90, self.prev_engine_val)

                    # temp_t = time%8-4
                    temp_t = time % 6 - 4
                    self.prev_secondary_rpm_val = abs(2 * temp_t * math.exp(temp_t)
                                                      - math.exp(1.65 * temp_t))
                    self.data.add_value(91, self.prev_secondary_rpm_val)

                    self.prev_lds_val = 100 + 100 * math.sin(time / 20)
                    self.data.add_value(92, self.prev_lds_val)

                    self.prev_br_lds_val = max(1800, min(4000, self.prev_engine_val + 0.5 * math.sin(
                        time * 10) + random.randrange(-2, 2)))
                    self.data.add_value(93, self.prev_br_lds_val)

                    self.prev_bl_lds_val = 100 + 100 * math.sin(time * 2) \
                                           + 100 * math.sin(time * 3.2) \
                                           + 100 * math.sin(time * 5.5) \
                                           + 100 * math.sin(time * 11.4)
                    self.data.add_value(94, self.prev_bl_lds_val)

                    self.prev_fr_lds_val = math.e ** (3 * math.sin(5 * time)) * abs(math.cos(5 * time)) + \
                                           50 * math.cos(time) \
                                           + 25 * math.cos(1 / 4 * time - math.pi / 6) \
                                           + 20 * math.cos(1 / 25 * time - math.pi / 3) \
                                           + 100 + random.randrange(-2, 2)
                    self.data.add_value(95, self.prev_fr_lds_val)
