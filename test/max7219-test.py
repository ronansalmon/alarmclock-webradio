#!usr/bin/env python

import time
import argparse

from PIL import ImageFont
from pathlib import Path
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text

print('Press Ctrl-C to quit...')

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='matrix_demo arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--cascaded', '-n', type=int, default=5, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=0, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')

    args = parser.parse_args()
    Tv = "22:59"

    for x in range(0, 255):
        print(x)
        device.contrast(x)
        with canvas(device) as draw:
            text(draw, (0, 0), Tv, fill="white")

        time.sleep(0.1)


