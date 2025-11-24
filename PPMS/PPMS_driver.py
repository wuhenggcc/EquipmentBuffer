import os
from PyQt5 import uic
from .PPMS_app import PPMSApp
# import MultiPyVu as mpv
import time, random

class PPMSDriver():
    def __init__(self, address):
        self.client = address
        self._method_map = {
            'field': self.get_field,
            'temperature': self.get_temperature,
        }

    def set_subscribes(self, subscribes: list):
        self.subscribes = subscribes

    def get_field(self):
        pass

    def get_temperature(self):
        pass

    def get_all(self):
        for sub in self.subscribes:
            self._method_map[sub]()
