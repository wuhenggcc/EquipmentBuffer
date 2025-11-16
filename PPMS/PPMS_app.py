from flask import Flask, jsonify, request
from werkzeug.serving import make_server
import threading
from general.equipment_buffer import EquipmentBuffer
from general.equipment_driver import FakeDriver
from werkzeug.serving import WSGIRequestHandler

class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


### a bug here is that this class use threading rather than PyQt6 QThread,
### which somehow will start buffer server multiple times if clicking start button repeatedly.
### This is temporary avoided by disabling start button when server is running.
### But a better solution is to refactor this to use QThread.
### Tried QThread, but seems not working, need to read more......

class PPMSApp():
    def __init__(self, buffer):
        # Initialize Flask and your equipment
        self.app = Flask(__name__)
        self.buffer = buffer

        # Create HTTP server and background thread placeholders
        self._server = None
        self._thread = None
        self._lock = threading.Lock()
        self._running = False
        # Define routes
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/")
        def home():
            return "<p>PPMS buffer layer, use /data to acquire data.</p>"

        @self.app.route("/data")
        def get_data():
            return jsonify(self.buffer.get_all())

        @self.app.route("/command", methods=["POST"])
        def command():
            data = request.json
            cmd = data.get("command")
            args = data.get("args", [])

            print(f"Received command: {cmd} with args: {args}")
            
            if not cmd:
                print("No command provided.")
                return jsonify({"error": "No command provided."}), 400
            self.buffer.send_command(cmd, *args)
            return jsonify({"status": "queued", "command": cmd})

    def start(self, host="127.0.0.1", port=5001):
        """Start the Flask app in a background thread."""
        with self._lock:
            if self._running:
                print("Server already running.")
                return
            self._running = True
        
        self.buffer.start()
        self._server = make_server(host, port, self.app, request_handler=QuietHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        print(f"PPMS buffer running on http://{host}:{port}")

    def stop(self):
        """Stop the Flask server cleanly."""
        with self._lock:
            if not self._running:
                print("No server running.")
                return
            self._running = False  # Mark stopped immediately

        print("Stopping PPMS buffer...")

        if self._server:
            self._server.shutdown()

        if self._thread:
            self._thread.join(timeout=2)
            
        self._server = None
        self._thread = None
        self.buffer.stop() 
        print("PPMS buffer stopped.")
