import os
import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PPMS.PPMS_app import PPMSApp
from PPMS.PPMS_driver import PPMSDriver
from PPMS.PPMS_behavior import PPMSBehavior, PPMSField, PPMSTemperature, PPMSRotator
from general.equipment_driver import FakeDriver
from general.equipment_buffer import EquipmentBuffer

ui_path = os.path.join('PPMS', 'widgets', 'PPMS_buffer.ui')
Ui_SequenceWindow, BaseClass = uic.loadUiType(ui_path)


class PPMSWindow(BaseClass, Ui_SequenceWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.field = PPMSField(self.widget_field)
        self.temperature = PPMSTemperature(self.widget_temperature)
        self.rotator = PPMSRotator(self.widget_rotator)

        self.label_support.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.label_support.setOpenExternalLinks(True)

        self.is_conected = False
        self.is_buffer_running = False
        self.is_flask_running = False
        self.is_query_running = False
        self._gui_state()

        self.buffer = None
        self.buffer_server = None
        self.behavior = None

        self.gb_field.setEnabled(False)
        self.gb_temperature.setEnabled(False)
        self.gb_rotator.setEnabled(False)

        self.pb_connect.clicked.connect(self.connect_driver)
        self.pb_disconnect.clicked.connect(self.disconnect_driver)
        self.pb_start_buffer.clicked.connect(self.start_buffer)
        self.pb_stop_buffer.clicked.connect(self.stop_buffer)
        self.pb_start_flask.clicked.connect(self.start_flask)
        self.pb_stop_flask.clicked.connect(self.stop_flask)
        self.pb_start_query.clicked.connect(self.start_query)
        self.pb_stop_query.clicked.connect(self.stop_query)

    def _gui_state(self):
        self.pb_connect.setEnabled(not self.is_conected)
        self.pb_disconnect.setEnabled(self.is_conected)
        self.pb_start_buffer.setEnabled(self.is_conected and not self.is_buffer_running)
        self.pb_stop_buffer.setEnabled(self.is_conected and self.is_buffer_running)
        self.gb_flask.setEnabled(self.is_conected and self.is_buffer_running)
        self.pb_start_flask.setEnabled(self.is_buffer_running and not self.is_flask_running)
        self.pb_stop_flask.setEnabled(self.is_buffer_running and self.is_flask_running)
        self.gb_query.setEnabled(self.is_flask_running)
        self.pb_start_query.setEnabled(self.is_flask_running and not self.is_query_running)
        self.pb_stop_query.setEnabled(self.is_flask_running and self.is_query_running)

    def connect_driver(self):
        address = self.le_address.text()
        self.driver = FakeDriver(address)
        self.is_conected = True
        self._gui_state()

    def disconnect_driver(self):
        """
        Disconnect the current driver.
        """
        self.driver = None
        self._gui_state()

    def start_buffer(self):
        self.pb_start_buffer.setEnabled(False)
        self.pb_stop_buffer.setEnabled(True)
        self.buffer = EquipmentBuffer(self.driver)
        self.buffer.start()
        self.is_buffer_running = True
        self._gui_state()
    
    def stop_buffer(self):
        if self.buffer:
            self.buffer.stop()
            self.buffer = None
        self.is_buffer_running = False
        self._gui_state()
    
    def start_flask(self):
        url = self.le_ip.text()
        port = self.sb_port.value()
        self.address = f"{url}:{port}"
        # Create and start buffer server
        self.buffer_server = PPMSApp(self.buffer)
        self.buffer_server.start(url, port)
        self.is_flask_running = True
        self._gui_state()

    def stop_flask(self):
        self.pb_start_buffer.setEnabled(True)
        self.pb_stop_buffer.setEnabled(False)
        if self.buffer_server:
            self.buffer_server.stop()
            self.buffer_server = None
        self.is_flask_running = False
        self._gui_state()

    def start_query(self):
        subscribe_list = {}
        if self.cb_field.isChecked():
            self.gb_field.setEnabled(True)
            subscribe_list['field']= self.field
        if self.cb_temperature.isChecked():
            self.gb_temperature.setEnabled(True)
            subscribe_list['temperature']= self.temperature
        if self.cb_rotator.isChecked():
            self.gb_rotator.setEnabled(True)
            subscribe_list['rotator']= self.rotator
        if not self.behavior:
            host = self.le_ip.text()
            port = self.sb_port.value()
            self.behavior = PPMSBehavior(host, port, subscribe_list)
            self.behavior.start_query()
        self.is_query_running = True
        self._gui_state()

    def stop_query(self):
        if self.behavior:
            self.behavior.stop_query()
        self.behavior = None
        self.is_query_running = False
        self._gui_state()

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PPMSWindow()
    window.show()
    sys.exit(app.exec())