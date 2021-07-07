"""
This file stores all the information needed for creating sensor objects

To add a sensor, add an element to the SensorId dictionary with the 
keyword being the id of that sensor. This should match the id that is
found in the SensorId.h file in the comms utility (DAQ>Libraries>Sensor).
Then add all the required parameters for that sensor along with any 
additional optional parameters.

Required parameters:
    - name
    - object
    - num_bytes

Optional parameters:
    - h_file_comment (not stored within Sensor)
    - name_multi     (required if multiple sensors are contained within the same ID)
    - is_float       (defaults to None)
    - display_name   (defaults to None)
    - unit           (defaults to None)
    - unit_short     (defaults to None)
    - is_plottable   (defaults to True)
    - is_external    (defaults to True)
    - class          (defaults to None)


Current classes:
    - dashboard
    - aux_daq
    - differential
    - engine_dyno
    - shock_dyno


"""


SensorId = {
    # 000 - DEFAULTS, FLAGS, COMMANDS, MISC
    0: {
        "name": "default_no_sensor",
        "object": "Generic",
        "num_bytes": 0,
        "is_float": False
    },
    1: {
        "name": "flag_datacollecting",
        "object": "Flag",
        "num_bytes": 1,
        "is_float": False
    },
    2: {
        "name": "command_sdcardfilenamestring",
        "object": "Command",
        "num_bytes": 12,
        "is_float": False
    },
    90: {
        "name": "test_sensor_0",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    91: {
        "name": "test_sensor_1",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    92: {
        "name": "test_sensor_2",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    93: {
        "name": "test_sensor_3",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    94: {
        "name": "test_sensor_4",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    95: {
        "name": "test_sensor_5",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    96: {
        "name": "test_sensor_6",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    97: {
        "name": "test_sensor_7",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    98: {
        "name": "test_sensor_8",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    99: {
        "name": "test_sensor_9",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    256: {
        "name": "test_sensor_10",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    257: {
        "name": "test_sensor_11",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    258: {
        "name": "test_sensor_12",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    259: {
        "name": "test_sensor_13",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    260: {
        "name": "test_sensor_14",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    261: {
        "name": "test_sensor_15",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    262: {
        "name": "test_sensor_16",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    263: {
        "name": "test_sensor_17",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    264: {
        "name": "test_sensor_18",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    265: {
        "name": "test_sensor_19",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    266: {
        "name": "test_sensor_20",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    267: {
        "name": "test_sensor_21",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },



    # 100 - TIME "SENSORS"
    100: {
        "name": "time_generic",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
    },
    101: {
        "name": "time_internal_seconds",
        "object": "Time",
        "num_bytes": 2,  # not 100% sure on this
        "display_name": "Time",
        "unit": "Seconds",
        "is_float": False,
        "unit_short": "s"
    },
    102: {
        "name": "time_dash_ms",
        "object": "Time",
        "num_bytes": 2,
        "display_name": "Dashboard Time Since Start",
        "unit": "Miliseconds",
        "unit_short": "ms",
        "is_float": False,
        "class": "dashboard"
    },
    103: {
        "name": "time_dash_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False,
        "class": "dashboard"
    },
    104: {
        "name": "time_auxdaq_ms",
        "object": "Time",
        "num_bytes": 2,
        "is_float": False,
        "class": "aux_daq"
    },
    105: {
        "name": "time_auxdaq_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False,
        "class": "aux_daq"
    },
    106: {
        "name": "time_diff_ms",
        "object": "Time",
        "num_bytes": 2,
        "is_float": False
    },
    107: {
        "name": "time_diff_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
    },
    108: {
        "name": "time_daata_ms",
        "object": "Time",
        "num_bytes": 2,
        "is_float": False
    },
    109: {
        "name": "time_daata_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
    },
    199: {
        "name": "rtc_unixtime",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
    },



    # 200 - SPEED/POSITION SENSORS
    200: {
        "name": "speed_generic",
        "object": "Speed",
        "num_bytes": 2,
        "pulses_per_revolution": 1,
        "is_float": False,
        "display_name": "Speed"
    },
    201: {
        "name": "position_generic",
        "object": "Position",
        "num_bytes": 4,
        "pulses_per_revolution": 1,
        "is_float": False,
        "display_name": "Position"
    },
    202: {
        "name": "speed_position_generic4",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (4ppr sensor)",
        0: {
            "name": "speed_generic4",
            "object": "Speed",
            "display_name": "Speed Generic (4ppr Sensor)",
            "pulses_per_revolution": 4,
            "is_float": False
        },
        1: {
            "name": "position_generic4",
            "object": "Position",
            "display_name": "Position Generic (4ppr Sensor)",
            "pulses_per_revolution": 4,
            "is_float": False
        }
    },
    203: {
        "name": "speed_position_generic30",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (30ppr sensor)",
        0: {
            "name": "speed_generic30",
            "object": "Speed",
            "display_name": "Speed Generic (30ppr Sensor)",
            "pulses_per_revolution": 4,
            "is_float": False
        },
        1: {
            "name": "position_generic30",
            "object": "Position",
            "display_name": "Position Generic (30ppr Sensor)",
            "pulses_per_revolution": 4,
            "is_float": False
        }
    },
    204: {
        "name": "speed_position_generic500",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (500ppr sensor)",
        0: {
            "name": "speed_generic500",
            "object": "Speed",
            "display_name": "Speed Generic (500ppr Sensor)",
            "pulses_per_revolution": 500,
            "is_float": False
        },
        1: {
            "name": "position_generic500",
            "object": "Position",
            "display_name": "Position Generic (500ppr Sensor)",
            "pulses_per_revolution": 500,
            "is_float": False
        }
    },
    205: {
        "name": "speed_position_generic600",
        "num_bytes": [4, 2],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "position_generic600",
            "object": "Position",
            "display_name": "Position Generic (600ppr Sensor)",
            "pulses_per_revolution": 600,
            "is_float": False
        },
        1: {
            "name": "speed_generic600",
            "object": "Speed",
            "display_name": "Speed Generic (600ppr Sensor)",
            "pulses_per_revolution": 600,
            "is_float": False
        }
    },
    206: {
        "name": "speed_position_engine600",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "speed_engine600",
            "object": "Speed",
            "display_name": "Speed Engine (600ppr Sensor)",
            "pulses_per_revolution": 600,
            "is_float": False,
            "class": "dashboard"
        },
        1: {
            "name": "position_engine600",
            "object": "Position",
            "display_name": "Position Engine (600ppr Sensor)",
            "pulses_per_revolution": 600,
            "is_float": False,
            "class": "dashboard"
        }
    },
    207: {
        "name": "speed_position_engine4",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (4ppr sensor)",
        0: {
            "name": "speed_engine4",
            "object": "Speed",
            "display_name": "Speed",
            "pulses_per_revolution": 4,
            "is_float": False,
            "class": "dashboard"
        },
        1: {
            "name": "position_engine4",
            "object": "Position",
            "display_name": "Position",
            "pulses_per_revolution": 4,
            "is_float": False,
            "class": "dashboard"
        }
    },
    208: {
        "name": "speed_position_secondary30",
        "num_bytes": [4, 4],
        "h_file_comment": "Speed in RPM and position in ticks (30ppr on gear)",
        0: {
            "name": "speed_secondary30",
            "object": "Speed",
            "display_name": "Speed",
            "pulses_per_revolution": 30,
            "is_float": False,
            "class": "dashboard"
        },
        1: {
            "name": "position_secondary30",
            "object": "Position",
            "display_name": "Position",
            "pulses_per_revolution": 30,
            "is_float": False,
            "class": "dashboard"
        }
    },
    209: {
        "name": "speed_engine600_rpm",
        "object": "Speed",
        "num_bytes": 2,
        "h_file_comment": "Speed in RPM (600ppr sensor)",
        "display_name": "Engine Speed",
        "unit": "Revolutions Per Minutes",
        "unit_short": "RPM",
        "pulses_per_revolution": 600,
        "is_float": False,
        "class": "dashboard"
    },
    210: {
        "name": "speed_engine4_rpm",
        "object": "Speed",
        "num_bytes": 2,
        "h_file_comment": "Speed in RPM (4ppr sensor)",
        "display_name": "Engine Speed",
        "unit": "Revolutions Per Minutes",
        "unit_short": "RPM",
        "pulses_per_revolution": 4,
        "is_float": False,
        "class": "dashboard"
    },
    211: {
        "name": "speed_secondary30_rpm",
        "object": "Speed",
        "num_bytes": 2,
        "h_file_comment": "Speed in RPM (30ppr sensor)",
        "display_name": "Engine Speed",
        "unit": "Revolutions Per Minutes",
        "unit_short": "RPM",
        "pulses_per_revolution": 30,
        "is_float": False,
        "class": "dashboard"
    },
    212: {
        "name": "speed_dynoengine600_rpm",
        "object": "Speed",
        "num_bytes": 2,
        "h_file_comment": "Speed in RPM (600ppr sensor)",
        "display_name": "Engine Speed",
        "unit": "Revolutions Per Minutes",
        "unit_short": "RPM",
        "pulses_per_revolution": 600,
        "is_float": False,
        "class": "engine_dyno"
    },
    213: {
        "name": "speed_dynosecondary30_rpm",
        "object": "Speed",
        "num_bytes": 2,
        "h_file_comment": "Speed in RPM (30ppr sensor)",
        "display_name": "Engine Speed",
        "unit": "Revolutions Per Minutes",
        "unit_short": "RPM",
        "pulses_per_revolution": 30,
        "is_float": False,
        "class": "engine_dyno"
    },
    
    # 300 - FORCE/PRESSURE SENSORS
    300: {
        "name": "pressure_generic",
        "object": "Pressure",
        "num_bytes": 2,
        "is_float": False
    },
    301: {
        "name": "force_generic",
        "object": "Force",
        "num_bytes": 4,
        "is_float": True
    },
    302: {
        "name": "brake_sensor1",
        "object": "Pressure",
        "num_bytes": 4,
        "is_float": False,
        "class": "aux_daq"
    },
    303: {
        "name": "brake_sensor2",
        "object": "Pressure",
        "num_bytes": 4,
        "is_float": False,
        "class": "aux_daq"
    },
    304: {
        "name": "pressure_frontbrake_psi",
        "object": "Pressure",
        "num_bytes": 2,
        "is_float": False,
        "class": "aux_daq"
    },
    305: {
        "name": "pressure_rearbrake_psi",
        "object": "Pressure",
        "num_bytes": 2,
        "is_float": False,
        "class": "aux_daq"
    },
    306: {
        "name": "force_dyno_lbs",
        "object": "Force",
        "num_bytes": 4,
        "is_float": True,
        "class": "engine_dyno"
    },



    # 400 - LDS SENSORS
    400: {
        "name": "lds_generic",
        "object": "LDS",
        "num_bytes": 2,
        "stroke_length": 1,
        "is_float": False
    },
    401: {
        "name": "lds_frontleftshock_mm",
        "object": "LDS",
        "num_bytes": 2,
        "stroke_length": 200,
        "is_float": False,
        "class": "aux_daq"
    },
    402: {
        "name": "lds_frontrightshock_mm",
        "object": "LDS",
        "num_bytes": 2,
        "stroke_length": 200,
        "is_float": False,
        "class": "aux_daq"
    },
    403: {
        "name": "lds_backleftshock_mm",
        "object": "LDS",
        "num_bytes": 2,
        "stroke_length": 225,
        "is_float": False,
        "class": "aux_daq"
    },
    404: {
        "name": "lds_backrightshock_mm",
        "object": "LDS",
        "num_bytes": 2,
        "stroke_length": 225,
        "is_float": False,
        "class": "aux_daq"
    },

    # 500 - IMU SENSORS
    500: {
        "name": "imu_sensor",
        "num_bytes": [4, 4, 4, 4, 4, 4, 4],
        #"is_float": [True, True, True, True, True, True, True],
        "h_file_comment": "Accel X, Y, Z; Gyro X, Y, Z; Temp",
        0: {
            "name": "imu_acceleration_x",
            "object": "Acceleration",
            "display_name": "IMU X Acceleration",
            "is_float": True,
            "class": "aux_daq"
        },
        1: {
            "name": "imu_acceleration_y",
            "object": "Acceleration",
            "display_name": "IMU Y Acceleration",
            "is_float": True,
            "class": "aux_daq"
        },
        2: {
            "name": "imu_acceleration_z",
            "object": "Acceleration",
            "display_name": "IMU Z Acceleration",
            "is_float": True,
            "class": "aux_daq"
        },
        3: {
            "name": "imu_gyro_x",
            "object": "Gyro",
            "display_name": "IMU X Gyro",
            "is_float": True,
            "class": "aux_daq"
        },
        4: {
            "name": "imu_gyro_y",
            "object": "Gyro",
            "display_name": "IMU Y Gyro",
            "is_float": True,
            "class": "aux_daq"
        },
        5: {
            "name": "imu_gyro_z",
            "object": "Gyro",
            "display_name": "IMU Z Gyro",
            "is_float": True,
            "class": "aux_daq"
        },
        6: {
            "name": "imu_temperature",
            "object": "Temperature",
            "display_name": "IMU Temperature",
            "is_float": True,
            "class": "aux_daq"
        }
    }
}
