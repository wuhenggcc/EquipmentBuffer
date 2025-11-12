import random
import time
import threading

class EquipmentBuffer:
    def __init__(self, driver, interval=0.1):
        self.driver = driver
        self.interval = interval
        self.cache = {}
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _poll_loop(self):
        while self.running:
            try:
                field = self.driver.get_field()
                temperature = self.driver.get_temperature()
                with self.lock:
                    self.cache = {
                        "field": field,
                        "temperature": temperature,
                        "timestamp": time.time(),
                    }
                    # print("Updated cache:", self.cache)
            except Exception as e:
                print("Polling error:", e)
            time.sleep(self.interval)

    def get_all(self):
        with self.lock:
            return dict(self.cache)


class FakeDriver:
    
    def get_field(self):
        time.sleep(0.1)
        return random.uniform(0, 1)
    
    def get_temperature(self):
        time.sleep(0.1)
        return random.uniform(4, 5)