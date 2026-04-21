import sys

from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class EquipmentSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Equipment")
        self.setModal(True)
        self.resize(320, 120)

        self.combo_equipment = QComboBox(self)
        self.combo_equipment.addItems(["PPMS", "TULIPS"])

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select the equipment to open:", self))
        layout.addWidget(self.combo_equipment)
        layout.addWidget(button_box)

    @property
    def selected_equipment(self):
        return self.combo_equipment.currentText()


def create_window(equipment_name):
    if equipment_name == "PPMS":
        from PPMS.PPMS_main import PPMSWindow 

        return PPMSWindow()
    if equipment_name == "TULIPS":
        from TULIPS.TULIPS_main import TULIPSWindow

        return TULIPSWindow()
    raise ValueError(f"Unsupported equipment: {equipment_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    selector = EquipmentSelectorDialog()
    if selector.exec() != QDialog.Accepted:
        sys.exit(0)

    window = create_window(selector.selected_equipment)
    window.show()
    sys.exit(app.exec())
