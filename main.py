import os
from PyQt6 import uic
import sys
import requests
from PyQt6.QtWidgets import QApplication
from PPMS.PPMS_app import PPMSApp
from PPMS.PPMS_driver import PPMSDriver
from PPMS.PPMS_requests import PPMSTemperatureBlock, PPMSField, PPMSTemperature

ui_path = os.path.join('PPMS', 'widgets', 'PPMS_buffer.ui')
Ui_SequenceWindow, BaseClass = uic.load_ui.loadUiType(ui_path)


class PPMSWindow(BaseClass, Ui_SequenceWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pb_start_buffer.clicked.connect(self.start_buffer)
        self.pb_stop_buffer.clicked.connect(self.stop_buffer)

        self.pb_start_query.clicked.connect(self.start_temp)

        self.field = PPMSField(self.widget_field)
        self.temperature = PPMSTemperature(self.widget_temperature)

    def connect_driver(self):
        self.client = PPMSDriver(self.address)

    def start_temp(self):
        self.temp = PPMSTemperatureBlock(self.temperature, self.field)

    def closeEvent(self, event):
        event.accept()

    def start_buffer(self):
        self.pb_start_buffer.setEnabled(False)
        self.pb_stop_buffer.setEnabled(True)
        url = self.le_listen_to.text()
        port = self.sb_port.value()
        self.address = f"{url}:{port}"
        # Create and start buffer server
        self.buffer_server = PPMSApp()
        self.buffer_server.start(url, port)

    def stop_buffer(self):
        self.pb_start_buffer.setEnabled(True)
        self.pb_stop_buffer.setEnabled(False)
        if self.buffer_server:
            self.buffer_server.stop()
            self.buffer_server = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PPMSWindow()
    window.show()
    sys.exit(app.exec())