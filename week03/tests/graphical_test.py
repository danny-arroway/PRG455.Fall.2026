
# SPDX-License-Identifier: MIT
#
# Ported from Adafruit's SSD1306 example sketch
# (Written by Limor Fried/Ladyada for Adafruit Industries, BSD license)
# https://github.com/adafruit/Adafruit_SSD1306
#
# This port targets the M5Stack CoreS3's built-in LCD (not an external
# SSD1306 OLED). It uses the CoreS3's M5GFX drawing API (M5.Lcd) instead of
# Adafruit_GFX, runs under UIFlow2 MicroPython, and reproduces the same
# sequence of drawing tests: lines, rects, circles, round rects, triangles,
# text, scrolling text, and a falling-bitmap ("snowflake") animation.
#
# Key differences from the original:

#   - M5.Lcd draws directly to the panel; there's no separate framebuffer,
#     so there's no equivalent of display.display() to call after drawing.
#   - There's no exposed 1-bit XBM bitmap draw, so draw_bitmap() below
#     walks the same byte array Adafruit used and plots pixels manually.
#   - CoreS3's M5GFX binding doesn't expose the SSD1306's hardware scroll
#     registers, so testscrolltext() fakes it by redrawing the string at
#     shifting x positions instead.
#   - There's no invertDisplay() in this API; testinvert() approximates it
#     with a screen flash rather than a true color inversion.
#   - cp437 isn't available, so testdrawchar() walks printable ASCII
#     (32-126) instead of the full extended character table.

import os, sys, io
import M5
from M5 import *
import time
import random

WHITE = 0xFFFFFF
BLACK = 0x000000

NUMFLAKES = 10
LOGO_WIDTH = 16
LOGO_HEIGHT = 16
logo_bmp = bytes([
    0b00000000, 0b11000000,
    0b00000001, 0b11000000,
    0b00000001, 0b11000000,
    0b00000011, 0b11100000,
    0b11110011, 0b11100000,
    0b11111110, 0b11111000,
    0b01111110, 0b11111111,
    0b00110011, 0b10011111,
    0b00011111, 0b11111100,
    0b00001101, 0b01110000,
    0b00011011, 0b10100000,
    0b00111111, 0b11100000,
    0b00111111, 0b11110000,
    0b01111100, 0b11110000,
    0b01110000, 0b01110000,
    0b00000000, 0b00110000,
])

flakes = []  # each entry: [x, y, dy]


def draw_bitmap(bitmap, x, y, w, h, color):
    # Manual plot of a 1bpp XBM-style bitmap (row-major, MSB first, rows
    # padded to whole bytes) since M5.Lcd has no built-in equivalent.
    byte_width = (w + 7) // 8
    for j in range(h):
        for i in range(w):
            b = bitmap[j * byte_width + (i // 8)]
            if b & (0x80 >> (i % 8)):
                M5.Lcd.drawPixel(x + i, y + j, color)


def testdrawline():
    w, h = M5.Lcd.width(), M5.Lcd.height()

    M5.Lcd.clear(BLACK)
    for i in range(0, w, 4):
        M5.Lcd.drawLine(0, 0, i, h - 1, WHITE)
    for i in range(0, h, 4):
        M5.Lcd.drawLine(0, 0, w - 1, i, WHITE)
    time.sleep_ms(250)

    M5.Lcd.clear(BLACK)
    for i in range(0, w, 4):
        M5.Lcd.drawLine(0, h - 1, i, 0, WHITE)
    for i in range(h - 1, -1, -4):
        M5.Lcd.drawLine(0, h - 1, w - 1, i, WHITE)
    time.sleep_ms(250)

    M5.Lcd.clear(BLACK)
    for i in range(w - 1, -1, -4):
        M5.Lcd.drawLine(w - 1, h - 1, i, 0, WHITE)
    for i in range(h - 1, -1, -4):
        M5.Lcd.drawLine(w - 1, h - 1, 0, i, WHITE)
    time.sleep_ms(250)

    M5.Lcd.clear(BLACK)
    for i in range(0, h, 4):
        M5.Lcd.drawLine(w - 1, 0, 0, i, WHITE)
    for i in range(0, w, 4):
        M5.Lcd.drawLine(w - 1, 0, i, h - 1, WHITE)
    time.sleep_ms(1500)


def testdrawrect():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    for i in range(0, h // 2, 2):
        M5.Lcd.drawRect(i, i, w - 2 * i, h - 2 * i, WHITE)
    time.sleep_ms(1500)


def testfillrect():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    n = 0
    for i in range(0, h // 2, 3):
        color = WHITE if n % 2 == 0 else BLACK
        M5.Lcd.fillRect(i, i, w - i * 2, h - i * 2, color)
        n += 1
    time.sleep_ms(1500)


def testdrawcircle():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    for i in range(0, max(w, h) // 2, 2):
        M5.Lcd.drawCircle(w // 2, h // 2, i, WHITE)
    time.sleep_ms(1500)


def testfillcircle():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    n = 0
    i = max(w, h) // 2
    while i > 0:
        color = WHITE if n % 2 == 0 else BLACK
        M5.Lcd.fillCircle(w // 2, h // 2, i, color)
        i -= 3
        n += 1
    time.sleep_ms(1500)


def testdrawroundrect():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    for i in range(0, h // 2 - 2, 2):
        M5.Lcd.drawRoundRect(i, i, w - 2 * i, h - 2 * i, h // 4, WHITE)
    time.sleep_ms(1500)


def testfillroundrect():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    n = 0
    for i in range(0, h // 2 - 2, 2):
        color = WHITE if n % 2 == 0 else BLACK
        M5.Lcd.fillRoundRect(i, i, w - 2 * i, h - 2 * i, h // 4, color)
        n += 1
    time.sleep_ms(1500)


def testdrawtriangle():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    for i in range(0, max(w, h) // 2, 5):
        M5.Lcd.drawTriangle(
            w // 2, h // 2 - i,
            w // 2 - i, h // 2 + i,
            w // 2 + i, h // 2 + i, WHITE)
    time.sleep_ms(1500)


def testfilltriangle():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    n = 0
    i = max(w, h) // 2
    while i > 0:
        color = WHITE if n % 2 == 0 else BLACK
        M5.Lcd.fillTriangle(
            w // 2, h // 2 - i,
            w // 2 - i, h // 2 + i,
            w // 2 + i, h // 2 + i, color)
        i -= 5
        n += 1
    time.sleep_ms(1500)


def testdrawchar():
    # No cp437 table available here, so this walks printable ASCII instead
    # of the Adafruit example's full extended character set.
    w = M5.Lcd.width()
    M5.Lcd.clear(BLACK)
    M5.Lcd.setTextSize(1)
    x, y = 0, 0
    for code in range(32, 127):
        M5.Lcd.setCursor(x, y)
        M5.Lcd.print(chr(code), WHITE)
        x += 6
        if x >= w - 6:
            x = 0
            y += 8
    time.sleep_ms(1500)


def testdrawstyles():
    M5.Lcd.clear(BLACK)

    M5.Lcd.setTextSize(1)
    M5.Lcd.setCursor(0, 0)
    M5.Lcd.print("Hello, world!", WHITE)

    M5.Lcd.setCursor(0, 10)
    M5.Lcd.print("3.141592", BLACK)  # matches original's "inverse" text idea,
    M5.Lcd.fillRect(0, 10, 60, 10, WHITE)  # via a light rect painted first
    M5.Lcd.setCursor(0, 10)
    M5.Lcd.print("3.141592", BLACK)

    M5.Lcd.setTextSize(2)
    M5.Lcd.setCursor(0, 24)
    M5.Lcd.print("0x%X" % 0xDEADBEEF, WHITE)
    time.sleep_ms(1500)
    M5.Lcd.setTextSize(1)


def testscrolltext():
    # M5.Lcd has no hardware scroll-register API on CoreS3, so this
    # reproduces the visual effect in software by redrawing the string.
    w = M5.Lcd.width()
    M5.Lcd.setTextSize(2)
    text = "scroll"
    text_w = len(text) * 12 * 2
    y = 10
    for x in range(w, -text_w, -4):
        M5.Lcd.clear(BLACK)
        M5.Lcd.setCursor(x, y)
        M5.Lcd.print(text, WHITE)
        time.sleep_ms(15)
    M5.Lcd.setTextSize(1)


def testdrawbitmap():
    w, h = M5.Lcd.width(), M5.Lcd.height()
    M5.Lcd.clear(BLACK)
    draw_bitmap(logo_bmp, (w - LOGO_WIDTH) // 2, (h - LOGO_HEIGHT) // 2,
                LOGO_WIDTH, LOGO_HEIGHT, WHITE)
    time.sleep_ms(1000)


def testinvert():
    # Approximation only -- there's no true invertDisplay() exposed here,
    # so this just flashes the palette to give a similar visual beat.
    M5.Lcd.clear(WHITE)
    time.sleep_ms(500)
    M5.Lcd.clear(BLACK)
    time.sleep_ms(500)


def setup():
    global flakes

    M5.begin()
    M5.Lcd.setRotation(1)
    M5.Lcd.clear(BLACK)

    testdrawline()
    testdrawrect()
    testfillrect()
    testdrawcircle()
    testfillcircle()
    testdrawroundrect()
    testfillroundrect()
    testdrawtriangle()
    testfilltriangle()
    testdrawchar()
    testdrawstyles()
    testscrolltext()
    testdrawbitmap()
    testinvert()

    # seed the falling-bitmap ("snowflake") animation state for loop()
    w = M5.Lcd.width()
    flakes = []
    for i in range(NUMFLAKES):
        flakes.append([
            random.randint(0, max(0, w - LOGO_WIDTH)),
            -LOGO_HEIGHT - random.randint(0, 40),
            random.randint(1, 5),
        ])


def loop():
    global flakes
    M5.update()

    w, h = M5.Lcd.width(), M5.Lcd.height()

    M5.Lcd.startWrite()
    M5.Lcd.clear(BLACK)
    for f in flakes:
        draw_bitmap(logo_bmp, f[0], f[1], LOGO_WIDTH, LOGO_HEIGHT, WHITE)
    M5.Lcd.endWrite()
    time.sleep_ms(80)

    for f in flakes:
        f[1] += f[2]
        if f[1] >= h:
            f[0] = random.randint(0, max(0, w - LOGO_WIDTH))
            f[1] = -LOGO_HEIGHT
            f[2] = random.randint(1, 5)


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