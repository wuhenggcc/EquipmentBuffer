import os

from PyQt5 import uic

from general.equipment_buffer import EquipmentBuffer
from .TULIPS_app import TULIPSApp
from .TULIPS_behavior import TULIPSBehavior, TULIPSRotator
from .TULIPS_driver import TULIPSDriver

ui_path = os.path.join("TULIPS", "widgets", "TULIPS_main.ui")
Ui_SequenceWindow, BaseClass = uic.loadUiType(ui_path)


class TULIPSWindow(BaseClass, Ui_SequenceWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("TULIPS buffer layer")

        self.rotator = TULIPSRotator(self.widget_rotator)

        self.is_conected = False
        self.is_buffer_running = False
        self.is_flask_running = False
        self.is_query_running = False

        self.driver = None
        self.buffer = None
        self.buffer_server = None
        self.behavior = None

        self.cb_temperature.setChecked(False)
        self.cb_temperature.setEnabled(False)
        self.cb_field.setChecked(False)
        self.cb_field.setEnabled(False)
        self.cb_rotator.setChecked(True)
        self.gb_rotator.setEnabled(False)
        self._gui_state()

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
        self.driver = TULIPSDriver(address)
        self.is_conected = True
        self._gui_state()

    def disconnect_driver(self):
        if self.driver:
            self.driver.disconnect()
        self.driver = None
        self.is_conected = False
        self._gui_state()

    def start_buffer(self):
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
        self.buffer_server = TULIPSApp(self.buffer)
        self.buffer_server.start(url, port)
        self.is_flask_running = True
        self._gui_state()

    def stop_flask(self):
        if self.behavior:
            self.behavior.stop_query()
            self.behavior = None
        self.is_query_running = False
        if self.buffer_server:
            self.buffer_server.stop()
            self.buffer_server = None
        self.buffer = None
        self.is_flask_running = False
        self.is_buffer_running = False
        self._gui_state()

    def start_query(self):
        subscribe_list = {}
        if self.cb_rotator.isChecked():
            self.gb_rotator.setEnabled(True)
            subscribe_list["rotator"] = self.rotator
        else:
            self.gb_rotator.setEnabled(False)
        if not self.behavior:
            host = self.le_ip.text()
            port = self.sb_port.value()
            self.behavior = TULIPSBehavior(host, port, subscribe_list)
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
        if self.behavior:
            self.behavior.stop_query()
        if self.buffer_server:
            self.buffer_server.stop()
            self.buffer_server = None
            self.buffer = None
        elif self.buffer:
            self.buffer.stop()
            self.buffer = None
        if self.driver:
            self.driver.disconnect()
        event.accept()
