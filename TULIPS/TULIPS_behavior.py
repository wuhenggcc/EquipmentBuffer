import os
import traceback

import requests
from PyQt5 import uic
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot


def load_ui_types(filename):
    path = os.path.join("TULIPS", "widgets", filename)
    return uic.loadUiType(path)


Ui_RotatorWidget, BaseClass = load_ui_types("TULIPS_rotator.ui")


class TULIPSBehavior:
    def __init__(self, host, port, subscribe_list) -> None:
        self.host = host
        self.port = port
        self.rotator_brick = subscribe_list.get("rotator", None)
        self.init_query_worker()

    def init_query_worker(self):
        if self.rotator_brick:
            self.rotator_brick.set_angle_args.connect(
                lambda args: self.send_command("set_angle", args)
            )
        self.client_thread = QThread()
        self.client = TULIPSQueryWorker(self.host, self.port)
        self.client.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client.start)
        self.client.data_received.connect(self.handle_data)
        self.client.connection_error.connect(self.handle_error)

    def start_query(self):
        self.client_thread.start()

    def handle_data(self, data):
        rotator_reading = data.get("rotator")
        if self.rotator_brick and rotator_reading is not None:
            self.rotator_brick.update_reading(rotator_reading)

    def handle_error(self, err):
        print("Connection error:", err)

    def stop_query(self):
        self.client.stop()
        self.client_thread.quit()
        self.client_thread.wait()

    def send_command(self, command, args):
        self.client.send_command(command, args)


class TULIPSRotator(BaseClass, Ui_RotatorWidget):
    set_angle_args = pyqtSignal(dict)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.reading_format = '<p><span style=" font-size:20pt; color:#00aa00;">{value}</span></p>'
        self.state_format = '<p><span style=" font-size:20pt; color:#00aa7f;">{state}</span></p>'

        self.label_reading = self.label_18
        self.label_state = self.label_19
        self.le_target = self.lineEdit_7
        self.pb_set = self.pushButton_13

        self.pb_set.clicked.connect(self.set_angle)

    def update_reading(self, rotator_reading):
        self.label_reading.setText(
            self.reading_format.format(value=str(rotator_reading[0]))
        )
        self.label_state.setText(
            self.state_format.format(state=str(rotator_reading[1]))
        )

    def set_angle(self):
        cmd_args = {
            "target": self.le_target.text(),
            "rate": "",
            "approach": "",
        }
        self.set_angle_args.emit(cmd_args)


class TULIPSQueryWorker(QObject):
    data_received = pyqtSignal(dict)
    connection_error = pyqtSignal(str)
    command_sent = pyqtSignal(dict)

    def __init__(self, host, port, interval=1000, parent=None):
        super().__init__(parent)
        self.url_data = f"http://{host}:{port}/data"
        self.url_cmd = f"http://{host}:{port}/command"
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self._request_data)
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.timer.start()

    def stop(self):
        if self.running:
            self.timer.stop()
            self.running = False

    @pyqtSlot()
    def _request_data(self):
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
