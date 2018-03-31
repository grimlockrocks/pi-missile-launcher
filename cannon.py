#!/usr/bin/python

import struct
import os
import sys
import platform
import time
import socket
import re
import json
import base64
import usb.core
import usb.util

from getch import getch, pause

# Protocol command bytes
DOWN    = 0x01
UP      = 0x02
LEFT    = 0x04
RIGHT   = 0x08
FIRE    = 0x10
STOP    = 0x20

DEVICE = None

# Setup the cannon
def setup_usb():
    
    # Find the device
    global DEVICE 
    DEVICE = usb.core.find(idVendor=0x2123, idProduct=0x1010)
    if DEVICE is None:
        DEVICE = usb.core.find(idVendor=0x0a81, idProduct=0x0701)
    if DEVICE is None:
        raise ValueError("Device not found")

    # On Linux we need to detach usb HID first
    if "Linux" == platform.system():
        try:
            DEVICE.detach_kernel_driver(0)
        except Exception as ex:
            pass # already unregistered    
    DEVICE.set_configuration()
    
    print(DEVICE)

# Control the LED light
# 1 -> on; 0 -> off
def led(status):
    DEVICE.ctrl_transfer(0x21, 0x09, 0, 0, [0x03, status, 0x00,0x00,0x00,0x00,0x00,0x00])

# Send command
def send_cmd(cmd):
    DEVICE.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])

# Send move command
def send_move(cmd):
    if cmd == FIRE:
        time.sleep(0.5)
        send_cmd(FIRE)
        time.sleep(4.5)
    else:
        send_cmd(cmd)
        time.sleep(0.2)
        send_cmd(STOP)

# Command mapping
def get_command(key):
    mapping = {
        "8": UP, 
        "4": LEFT,
        "6": RIGHT,
        "2": DOWN,
        "5": FIRE
    }
    return mapping.get(key)

def start():
    print("Setting up USB connection")
    setup_usb()
    print("Device is connected")
    led(1);

    print("Enter your command:")
    print("8->up; 4->left; 6->right; 2->down")
    print("5->fire")
    print("q->quit")
    while True:
        key = getch()
        if key == "q":
            print("Goodbye")
            led(0)
            break
        command = get_command(key)
        if command != None:
            send_move(command)

start()
