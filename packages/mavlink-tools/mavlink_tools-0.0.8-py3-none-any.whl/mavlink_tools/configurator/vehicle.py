#!/usr/bin/env python3
import os
import sys
import time
import math
import yaml
import serial
from pymavlink import mavutil
from pymavlink.mavutil import mavlink
from mavlink_tools.log_analyzer.color_logging import log_warn
from .mavlink_params import deserialize_param_value, float_to_integer, serialize_param_value

SOURCE_SYSTEM = 2
SOURCE_COMPONENT = 1
MAV_PARAM_TYPE_INT32 = 6
MAX_REQUESTED_SIZE = 90


class Vehicle:
    def __init__(self) -> None:
        self.device_path = None
        self.autopilot = None
        self.master = None
        self.params = None

    def connect(self):
        while True:
            try:
                self.device_path, self.autopilot = Vehicle._get_autopilot_path()
                if self.device_path is not None:
                    self._connect()
                    print(f"Connected: {self.device_path}")
                    break
            except serial.serialutil.SerialException:
                pass

            time.sleep(1)
            print(f"Waiting for the Autopilot {self.device_path}...")

    def configure(self, file_with_params, reboot=True):
        self._read_yaml_parameters(file_with_params)
        num_of_recv_params = 0

        print(f"Trying to write {len(self.params)} params...")
        for param_name in self.params:
            set_param_value = self.params[param_name]
            if self.set_specific_param(param_name, set_param_value):
                num_of_recv_params += 1
        print(f"Successfully written {num_of_recv_params}/{len(self.params)} params.")

        if reboot:
            time.sleep(2)
            self.reboot()
            time.sleep(2)
            self.connect()

    def download_px4_log(self, output_dir, output_file_name=""):
        myfile = open("log.ulg", "wb")

        self.master.mav.log_request_list_send(
            self.master.target_system,
            self.master.target_component,
            0,
            1024)
        log_entry_msg = self.master.recv_match(type='LOG_ENTRY', blocking=True)
        last_log_num = log_entry_msg.last_log_num
        last_log_size_kbytes = int(log_entry_msg.size / 1024)
        print(f"Last log number is {last_log_num}. The size is {last_log_size_kbytes} KBytes.")
        print(f"Output file will be: {output_dir}/{output_file_name}")

        start_time = time.time()

        for ofs in range(0, log_entry_msg.size, MAX_REQUESTED_SIZE):
            self.master.mav.log_request_data_send(
                self.master.target_system,
                self.master.target_component,
                id=last_log_num,
                ofs=ofs,
                count=MAX_REQUESTED_SIZE)

            log_data_msg = self.master.recv_match(type='LOG_DATA', blocking=True)

            data = bytearray(log_data_msg.data)
            myfile.write(data)

            sys.stdout.write("\033[K")
            identifier = log_data_msg.id
            ofs_kbytes = int(log_data_msg.ofs / 1024)
            elapsed_time = int(time.time() - start_time)
            msg = f"\r{identifier}, {elapsed_time} sec: {ofs_kbytes} / {last_log_size_kbytes} KB."
            print(msg, end='', flush=True)

            if log_data_msg.count < MAX_REQUESTED_SIZE:
                break

        myfile.close()
        print("")

    def read_all_params(self):
        self.master.mav.param_request_list_send(
            self.master.target_system, self.master.target_component
        )
        self.params = {}
        prev_recv_time_sec = time.time()
        while prev_recv_time_sec + 1.0 > time.time():
            time.sleep(0.01)
            recv_msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if recv_msg is not None:
                if recv_msg.param_type == MAV_PARAM_TYPE_INT32:
                    recv_msg.param_value = float_to_integer(recv_msg.param_value)
                recv_msg = recv_msg.to_dict()
                self.params[recv_msg['param_id']] = recv_msg['param_value']
                print(f"name: {recv_msg['param_id']} value: {recv_msg['param_value']}")
                prev_recv_time_sec = time.time()
        print("Done!")

    def read_specific_param(self, param_name, verbose=False, number_of_attempts=100):
        """Non-blocking read of the specific parameter. Several attemps until fail."""
        if verbose:
            print(f"{param_name: <18}", end = '', flush=True)

        recv_msg = None
        param_value = None
        for _ in range(number_of_attempts):
            self.master.mav.param_request_read_send(
                self.master.target_system,
                self.master.target_component,
                bytes(param_name, 'utf-8'),
                -1
            )

            recv_msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if recv_msg is None:
                time.sleep(0.1)
                continue

            recv_param_name, param_type, param_value = deserialize_param_value(recv_msg)
            if recv_param_name == param_name:
                if verbose:
                    print(f"{param_type: <6} {param_value}")
                break

        if recv_msg is None:
            log_warn(f'Reading {param_name} have been failed {number_of_attempts} times.')
        return param_value

    def set_specific_param(self, param_name, param_value, number_of_attempts=50):
        """Non-blocking set of the specific parameter. Return True in success, otherwise False."""
        self.master.mav.param_set_send(
            self.master.target_system,
            self.master.target_component,
            bytes(param_name, 'utf-8'),
            *serialize_param_value(param_value)
        )
        for _ in range(number_of_attempts):
            recv_msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if recv_msg is None:
                time.sleep(0.01)
                continue

            recv_param_name, recv_param_type, recv_param_value = deserialize_param_value(recv_msg)
            if recv_param_name != param_name:
                time.sleep(0.01)
                continue

            if math.isclose(recv_param_value, param_value, rel_tol=1e-4):
                print(f"{recv_param_name: <18} {recv_param_type: <6} {recv_param_value}")
                return True

            log_warn(f'{param_name}: expected {param_value}, received {recv_param_value}.')
            return False

        log_warn(f'Writing {param_name} have been failed {number_of_attempts} times.')
        return False

    def reset_params_to_default(self):
        self._reset_params_to_default()
        self.reboot()
        time.sleep(2)
        self.connect()

    def force_calibrate(self):
        param2 = 76
        param5 = 76
        self.master.mav.command_long_send(self.master.target_system, self.master.target_component,
                                          mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, 0,
                                          0, param2, 0, 0, param5, 0, 0)

    def reboot(self):
        self.master.reboot_autopilot()
        self.master.close()

    @staticmethod
    def _get_autopilot_path():
        serial_devices = os.popen('ls /dev/serial/by-id').read().splitlines()
        return Vehicle.get_autopilot_type_by_serial_devices(serial_devices)

    @staticmethod
    def get_autopilot_type_by_serial_devices(serial_devices):
        if len(serial_devices) < 1:
            return None, None

        device_path = None
        autopilot_type = None
        for serial_device in serial_devices:
            if -1 != serial_device.find("ArduPilot"):
                device_path = f"/dev/serial/by-id/{serial_device}"
                autopilot_type = "ArduPilot"
                break
            if -1 != serial_device.find("PX4"):
                device_path = f"/dev/serial/by-id/{serial_device}"
                autopilot_type = "PX4"
                break

        return device_path, autopilot_type

    def _reset_params_to_default(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE,
            0,
            2, -1, 0, 0, 0, 0, 0)

    def _read_yaml_parameters(self, filename, verbose=False):
        with open(filename, encoding='UTF-8') as file_descriptor:
            self.params = yaml.load(file_descriptor, Loader=yaml.FullLoader)

        if verbose:
            print(f"{filename} has : {self.params}")

    def _connect(self):
        self.master = mavutil.mavlink_connection(
            self.device_path,
            source_component=SOURCE_COMPONENT,
            source_system=SOURCE_SYSTEM)
        self.master.mav.heartbeat_send(
            type=mavlink.MAV_TYPE_CHARGING_STATION,
            autopilot=6,
            base_mode=12,
            custom_mode=0,
            system_status=4)
        self.master.wait_heartbeat()

        system_str = f"system {self.master.target_system}"
        component_str = f"component {self.master.target_component}"
        print(f"Heartbeat from system ({system_str} {component_str})")
