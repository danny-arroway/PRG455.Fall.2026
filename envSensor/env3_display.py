"""
ENV III Sensor (SHT30 + QMP6988) real-time display
M5Stack CoreS3 (K128) — Port B (I2C, Grove: SDA=G9, SCL=G8)
UIFlow2 / MicroPython — no user interaction required

Verified against m5stack/uiflow-micropython:
  m5stack/libs/unit/env.py            -> ENVUnit class, ENV_III=3
  examples/unit/env/env_cores3.py     -> ENVUnit(i2c=..., type=...) usage
  docs.m5stack.com CoreS3 pinout      -> Port B = SDA G9, SCL G8
"""

import os, sys, io
import time
import M5
from M5 import *
from machine import I2C, Pin
from unit import ENVUnit

M5.begin()

Widgets.fillScreen(0x222222)

# Port B on CoreS3: SDA = GPIO9, SCL = GPIO8
i2c0 = I2C(0, scl=Pin(8), sda=Pin(9), freq=100000)

env3 = None
try:
    env3 = ENVUnit(i2c=i2c0, type=3)  # type=3 -> ENV III (SHT30 + QMP6988)
except Exception:
    env3 = None

title_label = Widgets.Label("ENV III Sensor", 20, 10, 1.0, 0xFFFFFF, 0x222222, Widgets.FONTS.DejaVu18)

temp_label = Widgets.Label("Temp: -- C", 20, 60, 1.0, 0x00FF88, 0x222222, Widgets.FONTS.DejaVu24)
hum_label = Widgets.Label("Humidity: -- %", 20, 110, 1.0, 0x66CCFF, 0x222222, Widgets.FONTS.DejaVu24)
pres_label = Widgets.Label("Pressure: -- hPa", 20, 160, 1.0, 0xFFCC66, 0x222222, Widgets.FONTS.DejaVu24)

status_label = Widgets.Label("", 20, 210, 1.0, 0xFF5555, 0x222222, Widgets.FONTS.DejaVu18)

if env3 is None:
    status_label.setText("ENV III not detected on Port B")

while True:
    M5.update()
    if env3 is not None:
        try:
            temperature = env3.read_temperature()
            humidity = env3.read_humidity()
            pressure = env3.read_pressure()  # already returned in hPa

            temp_label.setText("Temp: %.1f C" % temperature)
            hum_label.setText("Humidity: %.1f %%" % humidity)
            pres_label.setText("Pressure: %.1f hPa" % pressure)
            status_label.setText("")
        except Exception as e:
            status_label.setText("Read error: %s" % str(e))
    time.sleep_ms(500)
