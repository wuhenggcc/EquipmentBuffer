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
    
    def set_field(self, target_field, ramp_rate, approach_method='linear'):
        print(f"Setting field to {target_field} T with a ramp rate of {ramp_rate} T/min using {approach_method} approach.")
    
    def set_temperature(self, target_temp, ramp_rate, approach_method='linear'):
        print(f"Setting temperature to {target_temp} K with a ramp rate of {ramp_rate} K/min using {approach_method} approach.")


