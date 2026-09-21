# SPDX-License-Identifier: MIT
#
# Lab 3 precursor -- CoreS3 / UIFlow2 MicroPython
#
# Displays every printable "extended ASCII" character (codes 32-126)
# in a fixed grid, cycling through three color schemes:
#   1) white text on black
#   2) red text on white
#   3) blue text on gray
# then repeats.
#
# C0/C1 control codes (0-31, 127+) are skipped since they have no
# printable glyph.

import os, sys, io
import M5
from M5 import *
import time

WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
BLUE = 0x0000FF
GRAY = 0x808080

# (foreground, background) for each screen, shown in this order
SCREENS = [
    (WHITE, BLACK),
    (RED, WHITE),
    (BLUE, GRAY),
]

CHARS = [chr(c) for c in range(32, 127)]

# Grid cell size in pixels. Generous relative to DejaVu12's average
# glyph width so wide characters (M, W, etc.) don't overlap the next
# cell; tune down if you want a denser table.
CELL_W = 12
CELL_H = 18
MARGIN = 4

screen_index = 0


def draw_char_table(fg, bg):
    M5.Lcd.clear(bg)
    M5.Lcd.setTextColor(fg, bg)

    cols = (M5.Lcd.width() - MARGIN * 2) // CELL_W
    col = 0
    row = 0
    for ch in CHARS:
        x = MARGIN + col * CELL_W
        y = MARGIN + row * CELL_H
        M5.Lcd.setCursor(x, y)
        M5.Lcd.print(ch, fg)
        col += 1
        if col >= cols:
            col = 0
            row += 1


def setup():
    M5.begin()
    M5.Lcd.setRotation(1)
    M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu12)
    M5.Lcd.setTextSize(1)
    draw_char_table(*SCREENS[0])


def loop():
    global screen_index
    M5.update()
    time.sleep_ms(3000)
    screen_index = (screen_index + 1) % len(SCREENS)
    draw_char_table(*SCREENS[screen_index])


if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg
            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")
