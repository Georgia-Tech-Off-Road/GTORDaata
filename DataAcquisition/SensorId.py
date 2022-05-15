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
    - is_float       (defaults to None)
    - display_name   (defaults to None)
    - unit           (defaults to None)
    - unit_short     (defaults to None)
    - is_plottable   (defaults to True)
    - is_external    (defaults to True)
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
    3: {
        "name": "command_toggle_teensy_led",
        "object": "Command",
        "num_bytes": 1
    },
    4: {
        "name": "command_tare_load_cell",
        "object": "Command",
        "num_bytes": 1
    },
    5: {
        "name": "command_motor_speed",
        "object": "Command",
        "num_bytes": 1
    },
    6: {
        "name": "command_motor_enable",
        "object": "Command",
        "num_bytes": 1
    },
    7: {
        "name": "command_scale_load_cell",
        "object": "Command",
        "num_bytes": 4,
        "is_float": True
    },
    8: {
        "name": "gps_sensor",
        "num_bytes": [4, 4, 4],
        "h_file_comment": "Contains lattitude, longitude, and speed (knots)",
        0: {
            "name": "gps_lattitude",
            "object": "GPS",
            "display_name": "GPS Lattitude",
            "orientation": "lattitude",
            "is_float": False
        },
        1: {
            "name": "gps_longitude",
            "object": "GPS",
            "display_name": "GPS Longitude",
            "orientation": "longitude",
            "is_float": False
        },
        2: {
            "name": "gps_speed",
            "object": "Speed",
            "display_name": "GPS Speed",
            "is_float": False
        }
    },
    9: {
        "name": "command_auxdaq_sdwrite",
        "object": "Command",
        "num_bytes": 1,
        "is_float": False
    },
    10: {
        "name": "flag_auxdaq_sdwrite",
        "object": "Flag",
        "num_bytes": 1,
        "is_float": False
    },
    11: {
        "name": "dashboard_gps_sensor",
        "num_bytes": [4, 4, 4],
        "h_file_comment": "ECEF X, Y, Z (in cm)",
        0: {
            "name": "gps_ecef_x",
            "object": "GPS",
            "display_name": "GPS ECEF X",
            "orientation": None,
            "unit": "Centimeters",
            "unit_short": "cm",
            "is_float": True
        },
        1: {
            "name": "gps_ecef_y",
            "object": "GPS",
            "display_name": "GPS ECEF Y",
            "orientation": None,
            "unit": "Centimeters",
            "unit_short": "cm",
            "is_float": True
        },
        2: {
            "name": "gps_ecef_z",
            "object": "GPS",
            "display_name": "GPS ECEF Z",
            "orientation": None,
            "unit": "Centimeters",
            "unit_short": "cm",
            "is_float": True
        }
    },
    90: {
        "name": "test_sensor_0",
        "display_name": "Test Sensor 0",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    91: {
        "name": "test_sensor_1",
        "display_name": "Test Sensor 1",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    92: {
        "name": "test_sensor_2",
        "display_name": "Test Sensor 2",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    93: {
        "name": "test_sensor_3",
        "display_name": "Test Sensor 3",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    94: {
        "name": "test_sensor_4",
        "display_name": "Test Sensor 4",
        "object": "Generic",
        "num_bytes": 4,
        "is_float": False
    },
    95: {
        "name": "test_sensor_5",
        "display_name": "Test Sensor 5",
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
        "is_float": False
    },
    103: {
        "name": "time_dash_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
    },
    104: {
        "name": "time_auxdaq_ms",
        "object": "Time",
        "num_bytes": 2,
        "is_float": False
    },
    105: {
        "name": "time_auxdaq_us",
        "object": "Time",
        "num_bytes": 4,
        "is_float": False
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
        "is_float": False
    },
    201: {
        "name": "position_generic",
        "object": "Position",
        "num_bytes": 4,
        "pulses_per_revolution": 1,
        "is_float": False
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
            "is_float": False
        },
        1: {
            "name": "position_engine600",
            "object": "Position",
            "display_name": "Position Engine (600ppr Sensor)",
            "pulses_per_revolution": 600,
            "is_float": False
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
            "is_float": False
        },
        1: {
            "name": "position_engine4",
            "object": "Position",
            "display_name": "Position",
            "pulses_per_revolution": 4,
            "is_float": False
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
            "is_float": False
        },
        1: {
            "name": "position_secondary30",
            "object": "Position",
            "display_name": "Position",
            "pulses_per_revolution": 30,
            "is_float": False
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
        "is_float": False
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
        "is_float": False
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
        "is_float": False
    },
    212: {
        "name": "speed_dynoengine600_rpm",
        "num_bytes": [4, 2],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "dyno_engine_position",
            "object": "Position",
            "display_name": "Position Dyno (600ppr Sensor)",
            "pulses_per_revolution": 600
        },
        1: {
            "name": "dyno_engine_speed",
            "object": "Speed",
            "display_name": "Speed Dyno (600ppr Sensor)",
            "pulses_per_revolution": 600
        }
    },
    213: {
        "name": "speed_dynosecondary30_rpm",
        "num_bytes": [4, 2],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "dyno_secondary_position",
            "object": "Position",
            "display_name": "Position Dyno (30ppr Sensor)",
            "pulses_per_revolution": 30
        },
        1: {
            "name": "dyno_secondary_speed",
            "object": "Speed",
            "display_name": "Speed Dyno (30ppr Sensor)",
            "pulses_per_revolution": 30
        }
    },
    214: {
        "name": "speed_2021car_engine600_rpm",
        "num_bytes": [4, 2],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "position_engine_ticks",
            "object": "Position",
            "display_name": "Position Engine (600ppr Sensor)",
            "pulses_per_revolution": 600
        },
        1: {
            "name": "speed_engine_rpm",
            "object": "Speed",
            "display_name": "Speed Engine (600ppr Sensor)",
            "pulses_per_revolution": 600
        }
    },
    215: {
        "name": "speed_2021car_secondary30_rpm",
        "num_bytes": [4, 2],
        "h_file_comment": "Speed in RPM and position in ticks (600ppr sensor)",
        0: {
            "name": "position_secondary_ticks",
            "object": "Position",
            "display_name": "Position Secondary (30ppr Sensor)",
            "pulses_per_revolution": 30
        },
        1: {
            "name": "speed_secondary_rpm",
            "object": "Speed",
            "display_name": "Speed Secondary (30ppr Sensor)",
            "pulses_per_revolution": 30
        }
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
        "is_float": False
    },
    303: {
        "name": "brake_sensor2",
        "object": "Pressure",
        "num_bytes": 4,
        "is_float": False
    },
    304: {
        "name": "pressure_frontbrake_psi",
        "object": "Pressure",
        "num_bytes": 4,
        "is_float": True
    },
    305: {
        "name": "pressure_rearbrake_psi",
        "object": "Pressure",
        "num_bytes": 4,
        "is_float": True
    },
    306: {
        "name": "force_enginedyno_lbs",
        "object": "Force",
        "num_bytes": 4,
        "is_float": True
    },
    307: {
        "name": "force_shockdyno_lbs",
        "object": "Force",
        "num_bytes": 4,
        "is_float": True
    },
    308: {
        "name": "wheel_force_transducer_analog_1",
        "num_bytes": [4, 4, 4, 4],
        "h_file_comment": "FX, FY, FZ, MX",
        0: {
            "name": "fx_analog",
            "object": "Force",
            "display_name": "Wheel Force X Analog",
            "is_float": True
        },
        1: {
            "name": "fy_analog",
            "object": "Force",
            "display_name": "Wheel Force Y Analog",
            "is_float": True
        },
        2: {
            "name": "fz_analog",
            "object": "Force",
            "display_name": "Wheel Force Z Analog",
            "is_float": True
        },
        3: {
            "name": "mx_analog",
            "object": "Gyro",
            "display_name": "Wheel Gyro X Analog",
            "is_float": True
        }
    },
    309: {
        "name": "wheel_force_transducer_analog_2",
        "num_bytes": [4, 4, 4, 4],
        "h_file_comment": "MY, MZ, Vel, Pos",
        0: {
            "name": "my_analog",
            "object": "Gyro",
            "display_name": "Wheel Gyro Y Analog",
            "is_float": True
        },
        1: {
            "name": "mz_analog",
            "object": "Gyro",
            "display_name": "Wheel Gyro Z Analog",
            "is_float": True
        },
        2: {
            "name": "velocity_analog",
            "object": "Speed",
            "pulses_per_revolution": 1,
            "display_name": "Wheel Velocity Analog",
            "is_float": True
        },
        3: {
            "name": "position_analog",
            "object": "Position",
            "pulses_per_revolution": 1,
            "display_name": "Wheel Position Analog",
            "is_float": True
        }
    },
    310: {
        "name": "wheel_force_transducer_analog_3",
        "num_bytes": [4, 4, 4, 4],
        "h_file_comment": "AccelX, AccelY",
        0: {
            "name": "accel_x_analog",
            "object": "Acceleration",
            "display_name": "Wheel Accel X Analog",
            "is_float": True
        },
        1: {
            "name": "accel_z_analog",
            "object": "Acceleration",
            "display_name": "Wheel Accel Z Analog",
            "is_float": True
        },
        2: {
            "name": "no_connect_1",
            "object": "Acceleration",
            "display_name": "No Connect 1",
            "is_float": True
        },
        3: {
            "name": "no_connect_2",
            "object": "Acceleration",
            "display_name": "No Connect 2",
            "is_float": True
        }
    },
    311: {
        "name": "force_straingauge_strain",
        "object": "Strain",
        "num_bytes": 4,
        "is_float": True
    },
    312: {
        "name": "loadcell_chassisstiffness_lbs",
        "display_name": "Chassis Stiffness Force",
        "object": "Force",
        "num_bytes": 4,
        "is_float": True
    },

    # 400 - LDS SENSORS
    400: {
        "name": "lds_generic",
        "object": "LDS",
        "num_bytes": 1,
        "stroke_length": 1,
        "is_float": False
    },
    401: {
        "name": "lds_frontleftshock_mm",
        "object": "LDS",
        "num_bytes": 4,
        "stroke_length": 200,
        "is_float": True
    },
    402: {
        "name": "lds_frontrightshock_mm",
        "object": "LDS",
        "num_bytes": 4,
        "stroke_length": 200,
        "is_float": True
    },
    403: {
        "name": "lds_backleftshock_mm",
        "object": "LDS",
        "num_bytes": 4,
        "stroke_length": 225,
        "is_float": True
    },
    404: {
        "name": "lds_backrightshock_mm",
        "object": "LDS",
        "num_bytes": 4,
        "stroke_length": 225,
        "is_float": True
    },
    405: {
        "name": "lds_shockdyno_mm",
        "object": "LDS",
        "num_bytes": 1,
        "stroke_length": 225,
        "is_float": False
    },
    406: {
        "name": "lds_pedal_mm",
        "display_name": "Pedal Position",
        "h_file_comment": "This sensor probably only used for testing day 4/2/22",
        "unit_short": "mm",
        "object": "LDS",
        "num_bytes": 4,
        "stroke_length": 200,
        "is_float": True
    },

    # 500 - IMU SENSORS
    500: {
        "name": "imu_sensor",
        "num_bytes": [4, 4, 4, 4, 4, 4, 4],
        "h_file_comment": "Accel X, Y, Z; Gyro X, Y, Z; Temp",
        0: {
            "name": "imu_acceleration_x",
            "object": "Acceleration",
            "display_name": "IMU X Acceleration",
            "is_float": True
        },
        1: {
            "name": "imu_acceleration_y",
            "object": "Acceleration",
            "display_name": "IMU Y Acceleration",
            "is_float": True
        },
        2: {
            "name": "imu_acceleration_z",
            "object": "Acceleration",
            "display_name": "IMU Z Acceleration",
            "is_float": True
        },
        3: {
            "name": "imu_gyro_x",
            "object": "Gyro",
            "display_name": "IMU X Gyro",
            "is_float": True
        },
        4: {
            "name": "imu_gyro_y",
            "object": "Gyro",
            "display_name": "IMU Y Gyro",
            "is_float": True
        },
        5: {
            "name": "imu_gyro_z",
            "object": "Gyro",
            "display_name": "IMU Z Gyro",
            "is_float": True
        },
        6: {
            "name": "imu_temperature",
            "object": "Temperature",
            "display_name": "IMU Temperature",
            "is_float": True
        }
    },
    501: {
        "name": "dashboard_imu_wt901",
        "num_bytes": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        "h_file_comment": "Accel X, Y, Z; Roll, Pitch, Yaw; Quaternion 1, 2, 3, 4",
        0: {
            "name": "dashboard_accel_x",
            "object": "Acceleration",
            "display_name": "IMU X Acceleration",
            "is_float": True
        },
        1: {
            "name": "dashboard_accel_y",
            "object": "Acceleration",
            "display_name": "IMU Y Acceleration",
            "is_float": True
        },
        2: {
            "name": "dashboard_accel_z",
            "object": "Acceleration",
            "display_name": "IMU Z Acceleration",
            "is_float": True
        },
        3: {
            "name": "dashboard_roll",
            "object": "Angle",
            "display_name": "IMU Roll",
            "is_float": True
        },
        4: {
            "name": "dashboard_pitch",
            "object": "Angle",
            "display_name": "IMU Pitch",
            "is_float": True
        },
        5: {
            "name": "dashboard_yaw",
            "object": "Angle",
            "display_name": "IMU Yaw",
            "is_float": True
        },
        6: {
            "name": "dashboard_quaternion_1",
            "object": "Angle",
            "display_name": "IMU Quaternion 1",
            "is_float": True
        },
        7: {
            "name": "dashboard_quaternion_2",
            "object": "Angle",
            "display_name": "IMU Quaternion 2",
            "is_float": True
        },
        8: {
            "name": "dashboard_quaternion_3",
            "object": "Angle",
            "display_name": "IMU Quaternion 3",
            "is_float": True
        },
        9: {
            "name": "dashboard_quaternion_4",
            "object": "Angle",
            "display_name": "IMU Quaternion 4",
            "is_float": True
        }
    },

    # 600 - MISC SENSORS
    600: {
        "name": "temperature",
        "object": "Temperature",
        "num_bytes": 4,
        "display_name": "Temperature",
        "is_float": True
    },
    601: {
        "name": "voltage",
        "object": "Voltage",
        "num_bytes": 4,
        "display_name": "Voltage",
        "is_float": True
    }
}
