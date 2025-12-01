import os
from PyQt5 import uic
from .PPMS_app import PPMSApp
import MultiPyVu as mpv
import numpy as np

class PPMSDriver():
    def __init__(self, address):
        self.address = address
        self.client =  mpv.Client(self.address)
        self.client.open()
        self._method_map = {
            'field': self.get_field,
            'temperature': self.get_temperature,
        }

    def set_subscribes(self, subscribes: list):
        self.subscribes = subscribes

    def get_field(self):
        try:
            value, state = self.client.get_field()
        except ValueError:
            value = np.nan
            state = 'unkown'
        return (value, state)

    def get_temperature(self):
        try:
            value, state = self.client.get_temperature()
        except ValueError:
            value = np.nan
            state = 'unkown'
        return (value, state)

    def get_all(self):
        for sub in self.subscribes:
            self._method_map[sub]()

    def set_temperature(self, target, rate, approach = 'fast_settle'):
        try:
            target = float(target)
            rate = float(rate)
        except Exception as e:
            raise ValueError(f"target and rate need to be numbers")
        # print(f"Setting temperature to {target} K with a ramp rate of {rate} K/min using {approach} approach.")
        if approach == "fast_settle":
            approach = mpv.Client.temperature.approach_mode.fast_settle
        elif approach == "no_overshoot":
            approach = mpv.Client.temperature.approach_mode.no_overshoot
        else:
            raise ValueError(f"set temperature has no approach mode of {approach}")
        self.client.set_temperature(target, rate, approach)

    def set_field(self, target, rate, approach = 'linear'):
        ## internal unit of PPMS field is 'Oe'
        ## internal unit of PPMS field ramp is 'Oe/s'
        try:
            target = float(target)
            rate = float(rate)
        except Exception as e:
            raise ValueError(f"target and rate need to be numbers")
        # print(f"Setting field to {target} T with a ramp rate of {rate} T/min using {approach} approach.")
        if approach == 'linear': 
            approach = mpv.Client.field.approach_mode.linear
        elif approach == 'oscillate':
            approach = mpv.Client.field.approach_mode.oscillate
        elif approach == "no o'shoot":
            approach = mpv.Client.field.approach_mode.no_overshoot
        else: 
            raise ValueError(f"set field has no approach mode of {approach}")
        self.client.set_field(target, rate, approach)

    def disconnect(self):
        self.client.close_client()