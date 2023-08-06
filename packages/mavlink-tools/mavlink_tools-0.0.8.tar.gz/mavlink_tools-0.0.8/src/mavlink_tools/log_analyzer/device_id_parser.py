#!/usr/bin/env python3

BUS_TYPE_TO_STRING = {
    0 : "unknown",
    1 : "i2c",
    2 : "spi",
    3 : "uavcan",
    4 : "sim",
    5 : "serial",
    6 : "mavlink",
}

DEV_TYPE_TO_STRING = {
    131: "diff_press_uavcan",
    133: "gps_uavcan",
    161: "gps_EMLID"
}

def print_dev_id(device_id, data):
    output_string = f"device_id={device_id}: "

    dev_type_value = data["devtype"]
    output_string += f"devtype={dev_type_value} ({DEV_TYPE_TO_STRING[dev_type_value]}), "

    address_value = data["address"]
    output_string += f"address={address_value}, "

    output_string += "bus=?, "

    bus_type_value = data["bus_type"]
    try:
        bus_type_name =  BUS_TYPE_TO_STRING[bus_type_value]
    except KeyError:
        bus_type_name = "error"
    output_string += f"bus_type={bus_type_value} ({bus_type_name})"

    print(output_string)

def parse_device_id(device_id, verbose=False):
    data = {}
    data["bus_type"] = device_id % 256
    data["devtype"] = (device_id >> 16) % 256
    data["address"] = (device_id >> 8) % 256

    data["bus"] = (device_id >> 24) % 256
    data["zero_byte"] = (device_id >> 24) % 256

    if verbose:
        print_dev_id(device_id, data)

    return data
