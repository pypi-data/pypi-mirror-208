#!/usr/bin/env python3
import os
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = SCRIPT_DIR.parent / "src"
sys.path.append(SRC_DIR.absolute().as_posix())

# pylint: disable=wrong-import-position
from mavlink_tools.configurator.vehicle import Vehicle

class TestConfiguration(unittest.TestCase):
    def test_get_autopilot_type_by_serial_devices_empty(self):
        serial_devices = []
        full_dev_path, autopilot_type = Vehicle.get_autopilot_type_by_serial_devices(serial_devices)
        self.assertEqual(full_dev_path, None)
        self.assertEqual(autopilot_type, None)

    def test_get_autopilot_type_by_serial_devices_px4(self):
        serial_devices = ['usb-3D_Robotics_PX4_FMU_v5.x_0-if00']
        full_dev_path, autopilot_type = Vehicle.get_autopilot_type_by_serial_devices(serial_devices)
        self.assertEqual(full_dev_path, '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v5.x_0-if00')
        self.assertEqual(autopilot_type, 'PX4')

    def test_get_autopilot_type_by_serial_devices_ardupilot(self):
        serial_devices = [
            'usb-ArduPilot_CUAVv5_3C0025000251383138373938-if00',
            'usb-ArduPilot_CUAVv5_3C0025000251383138373938-if02'
        ]
        full_dev_path, autopilot_type = Vehicle.get_autopilot_type_by_serial_devices(serial_devices)
        self.assertEqual(full_dev_path, '/dev/serial/by-id/' + serial_devices[0])
        self.assertEqual(autopilot_type, 'ArduPilot')

if __name__ == '__main__':
    unittest.main()
