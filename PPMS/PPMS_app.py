from general.equipment_app import EquipmentApp


class PPMSApp(EquipmentApp):
    def __init__(self, buffer):
        super().__init__(buffer, equipment_name="PPMS")
