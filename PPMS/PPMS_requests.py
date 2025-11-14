from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
import requests
import traceback
import os

ui_field_path = os.path.join('PPMS', 'widgets', 'PPMS_field.ui')
Ui_FieldWidget, BaseClass = uic.load_ui.loadUiType(ui_field_path)
ui_temperature_path = os.path.join('PPMS', 'widgets', 'PPMS_temperature.ui')
Ui_TemperatureWidget, BaseClass = uic.load_ui.loadUiType(ui_temperature_path)

class PPMSTemperatureBlock():
    def __init__(self, temperature_brick, field_brick) -> None:
        self.temperature_brick = temperature_brick
        self.field_brick = field_brick
        self.start_query()

    def start_query(self):
        # Setup client in a separate QThread
        self.client_thread = QThread()
        self.client = PPMSQueryWorker(host="127.0.0.1", port=5001, interval=2000)
        self.client.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client.start)
        self.client.data_received.connect(self.handle_data)
        self.client.connection_error.connect(self.handle_error)

        self.client_thread.start()

    def handle_data(self, data):
        field_reading = data.get('field')
        temperature_reading = data.get('temperature')
        self.temperature_brick.update_reading(temperature_reading)
        self.field_brick.update_reading(field_reading)
        print("Received:", data)

    def handle_error(self, err):
        print("Connection error:", err)


class PPMSField(BaseClass, Ui_FieldWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#ff5500;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#ffaa00;">{state}</span></p>'

    def update_reading(self, field_reading):
        self.label_reading.setText(self.reading_format.format(value = str(field_reading)))

class PPMSTemperature(BaseClass, Ui_TemperatureWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#0055ff;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#00aaff;">{state}</span></p>'

    def update_reading(self, field_reading):
        self.label_reading.setText(self.reading_format.format(value = str(field_reading)))



class PPMSQueryWorker(QObject):
    data_received = pyqtSignal(dict)
    connection_error = pyqtSignal(str)

    def __init__(self, host="127.0.0.1", port=5001, interval=1000, parent=None):
        """
        A client to periodically request data from the PPMS Flask buffer.
        :param host: Flask server address
        :param port: Flask server port
        :param interval: polling interval in ms
        """
        super().__init__(parent)
        self.url = f"http://{host}:{port}/data"
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self._request_data)
        self.running = False

    def start(self):
        """Start polling the Flask server."""
        if not self.running:
            self.running = True
            self.timer.start()

    def stop(self):
        """Stop polling."""
        if self.running:
            self.running = False
            self.timer.stop()

    def _request_data(self):
        """Send GET request to the Flask server."""
        try:
            response = requests.get(self.url, timeout=2)
            response.raise_for_status()
            data = response.json()
            self.data_received.emit(data)
        except Exception as e:
            msg = f"Request error: {e}\n{traceback.format_exc()}"
            print(msg)
            self.connection_error.emit(str(e))
