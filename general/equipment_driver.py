import time, random


class FakeDriver:
    
    def get_field(self):
        time.sleep(0.1)
        return random.uniform(0, 1)
    
    def get_temperature(self):
        time.sleep(0.1)
        return random.uniform(4, 5)
    
    def set_field(self, value):
        print(f"Setting field to {value} T")