import time
import threading
import queue
from werkzeug.serving import WSGIRequestHandler

class EquipmentBuffer:
    def __init__(self, driver, interval=0.5):
        self.driver = driver
        self.interval = interval
        self.cache = {}
        self.lock = threading.Lock()
        self.running = False

        self.command_queue = queue.Queue()
        self.readers = self._build_readers()

    def _build_readers(self):
        readers = {}
        for key in ("field", "temperature", "rotator"):
            method_name = f"get_{key}"
            method = getattr(self.driver, method_name, None)
            if callable(method):
                readers[key] = method
        return readers

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def stop(self):
        self.running = False


    def send_command(self, cmd, args):
        """Add a command to the queue."""
        self.command_queue.put((cmd, args))

    def _poll_loop(self):
        while self.running:
            # 1. Execute commands first
            self._process_commands()
            time.sleep(0.5)
            # 2. Then collect data
            try:
                cache = {}
                for key, reader in self.readers.items():
                    cache[key] = reader()
                    time.sleep(0.1)
                with self.lock:
                    cache["timestamp"] = time.time()
                    self.cache = cache
            except Exception as e:
                print("Polling error:", e)

            time.sleep(self.interval)

    def _process_commands(self):
        """Execute all pending commands."""
        while not self.command_queue.empty():
            cmd, args = self.command_queue.get()
            print(f"Processing command: {cmd} with args: {args}")
            try:
                method = getattr(self.driver, cmd)
                method(*args)
            except Exception as e:
                print("Command error:", e)

    def get_all(self):
        with self.lock:
            return dict(self.cache)
