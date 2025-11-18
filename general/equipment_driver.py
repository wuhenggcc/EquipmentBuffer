import time, random


class FakeDriver():
    def __init__(self, address):
        self.address = address
    
    def get_field(self):
        time.sleep(0.1)
        return random.uniform(0, 1)
    
    def get_temperature(self):
        time.sleep(0.1)
        return random.uniform(4, 5)
    
    def set_field(self, target, rate, approach='linear'):
        print(f"Setting field to {target} T with a ramp rate of {rate} T/min using {approach} approach.")
    
    def set_temperature(self, target, rate, approach='linear'):
        print(f"Setting temperature to {target} K with a ramp rate of {rate} K/min using {approach} approach.")
