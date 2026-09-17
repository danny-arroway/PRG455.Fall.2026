"""
ENV III Sensor (SHT30 + QMP6988) real-time display
M5Stack CoreS3 (K128) — Port B (I2C, Grove)
UIFlow2 / MicroPython — no user interaction required

SHT30  : temperature + humidity, I2C address 0x44
QMP6988: barometric pressure,     I2C address 0x70
"""

import M5
from M5 import *
from unit import SHT30Unit, QMP6988Unit
import time

M5.begin()

# PORT B on CoreS3 is the Grove I2C port; the Unit helper handles the
# pin mapping for named ports. Both sensors share the same I2C bus.
sht30 = None
qmp = None
try:
    sht30 = SHT30Unit(PORTB)
except Exception:
    sht30 = None

try:
    qmp = QMP6988Unit(PORTB)
except Exception:
    qmp = None

Widgets.fillScreen(0x222222)

title_label = Widgets.Label("ENV III Sensor", 20, 10, 1.0, 0xFFFFFF, 0x222222, Widgets.FONTS.DejaVu18)

temp_label = Widgets.Label("Temp: -- C", 20, 60, 1.0, 0x00FF88, 0x222222, Widgets.FONTS.DejaVu24)
hum_label = Widgets.Label("Humidity: -- %", 20, 110, 1.0, 0x66CCFF, 0x222222, Widgets.FONTS.DejaVu24)
pres_label = Widgets.Label("Pressure: -- hPa", 20, 160, 1.0, 0xFFCC66, 0x222222, Widgets.FONTS.DejaVu24)

status_label = Widgets.Label("", 20, 210, 1.0, 0xFF5555, 0x222222, Widgets.FONTS.DejaVu18)

missing = []
if sht30 is None:
    missing.append("SHT30")
if qmp is None:
    missing.append("QMP6988")
if missing:
    status_label.setText("Not detected: " + ", ".join(missing))

while True:
    M5.update()
    errors = []

    if sht30 is not None:
        try:
            temperature = sht30.get_temperature()
            humidity = sht30.get_humidity()
            temp_label.setText("Temp: %.1f C" % temperature)
            hum_label.setText("Humidity: %.1f %%" % humidity)
        except Exception as e:
            errors.append("SHT30: %s" % str(e))

    if qmp is not None:
        try:
            pressure = qmp.get_pressure() / 100.0  # Pa -> hPa
            pres_label.setText("Pressure: %.1f hPa" % pressure)
        except Exception as e:
            errors.append("QMP6988: %s" % str(e))

    if errors:
        status_label.setText(" | ".join(errors))
    elif not missing:
        status_label.setText("")

    time.sleep_ms(500)
