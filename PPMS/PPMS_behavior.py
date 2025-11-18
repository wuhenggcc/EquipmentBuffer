from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
import requests
import traceback
import os

def load_ui_types(filename):
    path = os.path.join('PPMS', 'widgets', filename)
    return uic.loadUiType(path)

Ui_FieldWidget, BaseClass = load_ui_types('PPMS_field.ui')
Ui_TemperatureWidget, BaseClass = load_ui_types('PPMS_temperature.ui')
Ui_RotatorWidget, BaseClass = load_ui_types('PPMS_rotator.ui')

class PPMSBehavior():
    def __init__(self, subscribe_list) -> None:
        self.field_brick = subscribe_list.get('field', None)
        self.temperature_brick = subscribe_list.get('temperature', None)
        self.rotator_brick = subscribe_list.get('rotator', None)
        
        self.field_brick.set_field_args.connect(lambda args: self.send_command("set_field", args))
        self.temperature_brick.set_temperature_args.connect(lambda args: self.send_command("set_temperature", args))
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

        # print("Received:", data)

    def handle_error(self, err):
        print("Connection error:", err)

    def stop_query(self):
        self.client.stop()
        self.client_thread.quit()
        self.client_thread.wait()

    def send_command(self, command, args):
        self.client.send_command(command, args)


class PPMSField(BaseClass, Ui_FieldWidget):
    set_field_args = pyqtSignal(dict)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#ff5500;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#ffaa00;">{state}</span></p>'

        self.pb_set.clicked.connect(self.set_field)

    def update_reading(self, field_reading):
        self.label_reading.setText(self.reading_format.format(value = str(field_reading)))

    def set_field(self):
        target = self.le_target.text()
        rate = self.le_ramp_rate.text()
        approach = self.cob_approach.currentText()
        cmd_args = {
            "target": target,
            "rate": rate,
            "approach": approach,
        }
        self.set_field_args.emit(cmd_args)

class PPMSTemperature(BaseClass, Ui_TemperatureWidget):
    set_temperature_args = pyqtSignal(dict)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#0055ff;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#00aaff;">{state}</span></p>'
        self.pb_set.clicked.connect(self.set_temperature)

    def update_reading(self, field_reading):
        self.label_reading.setText(self.reading_format.format(value = str(field_reading)))

    def set_temperature(self):
        target = self.le_target.text()
        rate = self.le_ramp_rate.text()
        approach = self.cob_approach.currentText()
        cmd_args = {
            "target": target,
            "rate": rate,
            "approach": approach,
        }
        self.set_temperature_args.emit(cmd_args)

class PPMSRotator(BaseClass, Ui_RotatorWidget):
    """ not implemented yet """
    set_angle_args = pyqtSignal(dict)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#0055ff;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#00aaff;">{state}</span></p>'

    def update_reading(self, field_reading):
        self.label_reading.setText(self.reading_format.format(value = str(field_reading)))

    def set_angle(self):
        target = self.le_target.text()
        rate = self.le_ramp_rate.text()
        approach = self.cob_approach.currentText()
        cmd_arg = {
            "target": target,
            "rate": rate,
            "approach": approach,
        }
        self.set_angle_args.emit(cmd_arg)

class PPMSQueryWorker(QObject):
    data_received = pyqtSignal(dict)
    connection_error = pyqtSignal(str)
    command_sent = pyqtSignal(dict) 

    def __init__(self, host="127.0.0.1", port=5001, interval=1000, parent=None):
        """
        A client to periodically request data from the PPMS Flask buffer.
        :param host: Flask server address
        :param port: Flask server port
        :param interval: polling interval in ms
        """
        super().__init__(parent)
        self.url_data = f"http://{host}:{port}/data"
        self.url_cmd = f"http://{host}:{port}/command"
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
            response = requests.get(self.url_data, timeout=2)
            response.raise_for_status()
            data = response.json()
            self.data_received.emit(data)
        except Exception as e:
            msg = f"Request error: {e}\n{traceback.format_exc()}"
            print(msg)
            self.connection_error.emit(str(e))

    
    @pyqtSlot(str, dict)
    def send_command(self, cmd, args=None):
        """Send a command to the PPMS Flask server."""
        if args is None:
            args = {}
        try:
            payload = {"command": cmd, "args": args}
            print("Sending command:", payload)
            response = requests.post(self.url_cmd, json=payload, timeout=3)
            response.raise_for_status()
            data = response.json()
            self.command_sent.emit(data)
        except Exception as e:
            msg = f"Command error: {e}\n{traceback.format_exc()}"
            print(msg)
            self.connection_error.emit(str(e))