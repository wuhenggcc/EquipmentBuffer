import sys
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel


class TestWorking(QObject):
    msg = pyqtSignal(str)

    def __init__(self, timer, interval=500):
        super().__init__()
        self.timer = timer
        self.timer.setInterval(interval)
        self.count = 0
        self.timer.timeout.connect(self.do_work)
        self._running = False
        # self.timer.moveToThread(self.thread())

    @pyqtSlot()
    def do_work(self):
        self.count += 1
        self.msg.emit(f"working... count = {self.count}")

    def start(self):
        if not self._running:
            self._running = True
            self.timer.start()

    def stop(self):
        if self._running:
            self._running = False
            self.timer.stop()



class WorkController:
    def __init__(self):
        timer = QTimer()
        self.worker = TestWorking(timer, interval=500)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.msg.connect(self.print_msg)
        self.worker_thread.start()


    def start_work(self):
        self.worker.start()

    def stop_work(self):
        self.worker.stop()

    def print_msg(self, msg):
        print(msg)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worker Controller")
        self.controller = WorkController()

        # UI Elements
        self.label = QLabel("Status: Idle")
        self.start_btn = QPushButton("Start Work")
        self.stop_btn = QPushButton("Stop Work")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

        # Connect buttons
        self.start_btn.clicked.connect(self.start_work)
        self.stop_btn.clicked.connect(self.stop_work)

        # Connect worker signal to update label
        # self.controller.worker.msg.connect(self.update_label)

    def start_work(self):
        self.controller.start_work()
        self.label.setText("Status: Working...")

    def stop_work(self):
        self.controller.stop_work()
        self.label.setText("Status: Stopped")

    def update_label(self, msg):
        self.label.setText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())