import numpy as np

from .positioner_driver import PositionerDriver


class TULIPSDriver:
    def __init__(self, address):
        self.address = address
        self.client = PositionerDriver(address)
        self.client.connect()
        self.client.init()
        self._state = "idle"

    def get_rotator(self):
        try:
            angle = self.client.angle
            return (angle, self._state)
        except Exception:
            return (np.nan, "unknown")

    def set_angle(self, target):
        try:
            target = float(target)
        except Exception as exc:
            raise ValueError("target needs to be a number") from exc

        self._state = "moving"
        try:
            self.client.angle = target
        finally:
            self._state = "idle"

    def disconnect(self):
        if getattr(self.client, "ser", None) and self.client.ser.is_open:
            self.client.ser.close()
