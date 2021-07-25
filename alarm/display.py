from adafruit_ht16k33.segments import BigSeg7x4
import board
from datetime import datetime
import time


class Display:
    def __init__(self):
        self.i2c = board.I2C()
        self.display = BigSeg7x4(self.i2c)
        self.display.brightness = 0

    def show_time(self):
        while 1:
            self.display.print(datetime.now().strftime("%H:%M"))
            time.sleep(5)
