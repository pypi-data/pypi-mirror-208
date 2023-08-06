#!/usr/bin/env python3
import os
import sys
import unittest
from pathlib import Path
from collections import namedtuple

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = SCRIPT_DIR.parent / "src"
sys.path.append(SRC_DIR.absolute().as_posix())

# pylint: disable=wrong-import-position
from mavlink_tools.configurator.mavlink_params import deserialize_param_value, \
                                                      serialize_param_value, \
                                                      integer_to_float

MavlinkMessage = namedtuple('MavlinkMessage', 'param_id param_type param_value')

class TestMavlinkParams(unittest.TestCase):
    def test_deserialize_param_value(self):
        test_case_int = MavlinkMessage('SYS_AUTOSTART', 6, 1.8216880036222622e-41)
        _, _, recv_param_value = deserialize_param_value(test_case_int)
        self.assertEqual(recv_param_value, 13000)

        test_case_float = MavlinkMessage('CAL_GYRO0_XOFF', 9, 1.0)
        _, _, recv_param_value = deserialize_param_value(test_case_float)
        self.assertEqual(recv_param_value, 1.0)

    def test_serialize_param_value(self):
        self.assertEqual((1.8216880036222622e-41, 6), serialize_param_value(13000))
        self.assertEqual((1.0, 9), serialize_param_value(1.0))

    def test_integer_to_float(self):
        self.assertEqual(1.8216880036222622e-41, integer_to_float(13000))
        # self.assertEqual(-1.8216880036222622e-41, integer_to_float(-1))

if __name__ == '__main__':
    unittest.main()
