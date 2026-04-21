from general.equipment_app import EquipmentApp


class TULIPSApp(EquipmentApp):
    def __init__(self, buffer):
        super().__init__(buffer, equipment_name="TULIPS")
