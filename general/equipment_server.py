import threading
import time
import random
from flask import Flask, jsonify

class EquipmentServer:
    def __init__(self, driver, interval=0.1, host="0.0.0.0", port=5000):
        self.driver = driver
        self.interval = interval
        self.cache = {}
        self.app = Flask(__name__)
        self._polling = False
        self._thread = None
        self.host = host
        self.port = port

        # Flask routes
        @self.app.route("/data")
        def get_data():
            return jsonify(self.cache)

    def start(self):
        if not self._polling:
            self._polling = True
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()

        # Start Flask (non-blocking)
        threading.Thread(target=self.app.run, kwargs={
            "host": self.host, "port": self.port, "debug": False, "use_reloader": False
        }, daemon=True).start()

    def stop(self):
        self._polling = False

    def _poll_loop(self):
        while self._polling:
            try:
                field = self.driver.get_field()
                temperature = self.driver.get_temperature()
                self.cache = {
                    "field": field,
                    "temperature": temperature,
                    "timestamp": time.time()
                }
            except Exception as e:
                print("Polling error:", e)
            time.sleep(self.interval)


class FakeDriver:
    def get_field(self):
        time.sleep(0.5)
        return random.uniform(0, 1)

    def get_temperature(self):
        time.sleep(0.5)
        return random.uniform(4, 5)


if __name__ == "__main__":
    driver = FakeDriver()
    server = EquipmentServer(driver)
    server.start()
    print("Server started at http://127.0.0.1:5000/data")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
