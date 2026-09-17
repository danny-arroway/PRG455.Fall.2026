"""
ENV III Sensor (SHT30 + QMP6988) real-time display
M5Stack CoreS3 (K128) — Port B (I2C, Grove)
UIFlow2 / MicroPython — no user interaction required

SHT30  : temperature + humidity
QMP6988: barometric pressure
"""

import M5
from M5 import *
from unit import ENVIIIUnit
import time

M5.begin()

# PORT B on CoreS3 is the Grove I2C port; the Unit helper handles the
# pin mapping for named ports.
try:
    env3 = ENVIIIUnit(PORTB)
except Exception:
    env3 = None

Widgets.fillScreen(0x222222)

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
            pressure = env3.read_pressure() / 100.0  # Pa -> hPa

            temp_label.setText("Temp: %.1f C" % temperature)
            hum_label.setText("Humidity: %.1f %%" % humidity)
            pres_label.setText("Pressure: %.1f hPa" % pressure)
            status_label.setText("")
        except Exception as e:
            status_label.setText("Read error: %s" % str(e))
    time.sleep_ms(500)
