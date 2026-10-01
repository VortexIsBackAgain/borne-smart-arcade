#!/usr/bin/env python3
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device
Device.pin_factory = LGPIOFactory()

from gpiozero import Button
from signal import pause
import subprocess

PIN_HOME = 4
PIN_SHUTDOWN = 23
SHUTDOWN_HOLD_SECONDS = 3

btn_home = Button(PIN_HOME, pull_up=True, bounce_time=0.1)
btn_shutdown = Button(PIN_SHUTDOWN, pull_up=True, hold_time=SHUTDOWN_HOLD_SECONDS)

def go_home():
    subprocess.run(["sudo", "systemctl", "isolate", "arcade-menu.target"])
    subprocess.run(["sudo", "systemctl", "restart", "smart-arcade-menu.service"])

def do_shutdown():
    subprocess.run(["sudo", "shutdown", "-h", "now"])

btn_home.when_pressed = go_home
btn_shutdown.when_held = do_shutdown

pause()
