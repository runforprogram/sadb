#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, unicode_literals

import re
import subprocess
import sys
from distutils.spawn import find_executable
from pprint import pprint

adb_path = find_executable("adb")

if not adb_path:
    print('adb path not found.')
    exit(-1)

if sys.version_info.major == 2:
    input = raw_input


def sadb():
    devices, outputs = read_devices()
    args = read_args()
    device_count = len(devices)
    if len(args) == 0:
        print('just use sadb as an alias for adb')
        exit(-1)
    if args[0] == 'devices':
        cmd = [adb_path]
        cmd += args
        subprocess.call(cmd)
        exit(0)

    if device_count > 1:
        nums = select_devices(devices)
        for seq in nums:
            exec_adb_cmd_on_device(devices[seq], args)
    elif device_count == 1:
        exec_adb_cmd_on_device(devices[0], args)
    else:
        print("No device found")
        exit(-1)


def select_devices(devices):
    """ 选择设备 """
    device_count = len(devices)
    print("Device list:")
    print("0) All devices")
    for i, d in enumerate(devices, start=1):
        print("%d) %s\t%s" % (i, d['serial'], d['product']))
    print("q) Exit this operation")
    selected = input("\nselect: ")
    if selected == '0':
        nums = range(0, device_count)
    elif selected == 'q':
        print("Exit this operation")
        exit(-1)
    else:
        nums = []
        for i in re.split(r'[\s+,]', selected):
            if i.isdigit():
                seq = int(i) - 1
                if 0 <= seq < device_count:
                    nums.append(seq)
                    continue
            print("error input: %s, retry again\n" % i)
            return select_devices(devices)
    return nums


def read_args():
    """ 读取参数 """
    return sys.argv[1:]


def get(str,key):
    if key in str:
        return str[str.index(key)+len(key)+len(":"):str.index(" ",str.index(key),len(str)-1)]
    return str[0:str.index(" ")]

def read_devices():
    """ 读取设备列表 """
    devices = []
    outputs = []
    proc = subprocess.Popen([adb_path, 'devices', '-l'], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline().decode('utf-8').strip()
        outputs.append(line)
        if not line:
            break
        if line.strip() and not line.startswith('List of devices'):
            devices.append({
                'serial': get(line,"serial"),
                'product': get(line,"product"),
            })

    return devices, outputs


def exec_adb_cmd_on_device(device, args):
    """ 执行 adb 命令 """
    cmd = [adb_path, "-s", device['serial']]
    cmd += args
    print('\n[{product}]exec: adb -s {serial} {cmd}'.format(cmd=' '.join(args), serial=device['serial'], product=device['product']))
    subprocess.call(cmd)


def dd(obj):
    """ just for debug. """
    print(obj)
    exit(0)
