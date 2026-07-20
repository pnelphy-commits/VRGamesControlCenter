from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from services.quest_setup_service import QuestSetupService
from services.station_manager import StationManager


class QuestSetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_service = QuestSetupService()
        self.station_manager = StationManager()

        self.setWindowTitle("Meta Quest Setup Wizard")
        self.setMinimumWidth(520)

        self.setStyleSheet("""
            QDialog {
                background-color: #080B14;
            }

            QLabel {
                color: white;
                font-size: 14px;
            }

            QComboBox {
                background-color: #242B3A;
                color: white;
                border: 1px solid #37415A;
                border-radius: 8px;
                min-height: 38px;
                padding: 4px 10px;
            }

            QPushButton {
                background-color: #242B3A;
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 40px;
                padding: 6px 12px;
                font-weight: bold;
            }

            QPushButton#primaryButton {
                background-color: #6C4DFF;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(16)

        title = QLabel("META QUEST SETUP WIZARD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        instructions = QLabel(
            "Conecta una Meta Quest por USB, acepta la depuración "
            "y selecciona la estación que deseas asignar."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #8992A9;")

        self.device_label = QLabel("Visor USB: No detectado")
        self.device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.station_selector = QComboBox()
        self.station_selector.addItems(
            [
                "META QUEST 1",
                "META QUEST 2",
                "META QUEST 3",
                "META QUEST 4",
            ]
        )

        buttons_layout = QHBoxLayout()

        refresh_button = QPushButton("BUSCAR VISOR")
        refresh_button.clicked.connect(self.refresh_usb_devices)

        configure_button = QPushButton("CONFIGURAR POR WIFI")
        configure_button.setObjectName("primaryButton")
        configure_button.clicked.connect(self.configure_device)

        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(configure_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(instructions)
        main_layout.addWidget(self.device_label)
        main_layout.addWidget(self.station_selector)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.result_label)

        self.usb_serial = ""
        self.refresh_usb_devices()

    def refresh_usb_devices(self):
        devices = self.setup_service.get_usb_devices()

        if not devices:
            self.usb_serial = ""
            self.device_label.setText("Visor USB: No detectado")
            self.device_label.setStyleSheet("color: #FF5C77;")
            return

        self.usb_serial = devices[0]
        self.device_label.setText(
            f"Visor USB detectado: {self.usb_serial}"
        )
        self.device_label.setStyleSheet("color: #3DDC84;")

    def configure_device(self):
        if not self.usb_serial:
            QMessageBox.warning(
                self,
                "Sin visor",
                "Conecta una Meta Quest por USB y pulsa BUSCAR VISOR.",
            )
            return

        station_number = self.station_selector.currentIndex() + 1

        self.result_label.setText("Configurando visor...")
        self.result_label.setStyleSheet("color: #F5B041;")

        result = self.setup_service.configure_usb_device(
            self.usb_serial
        )

        if not result:
            self.result_label.setText(
                self.setup_service.last_error
            )
            self.result_label.setStyleSheet("color: #FF5C77;")
            return

        self.station_manager.assign_station(
            station_number=station_number,
            serial=result["serial"],
            ip=result["ip"],
        )

        self.result_label.setText(
            f"META QUEST {station_number} configurada correctamente.\n"
            f"Serial: {result['serial']}\n"
            f"IP: {result['ip']}"
        )
        self.result_label.setStyleSheet("color: #3DDC84;")

        QMessageBox.information(
            self,
            "Configuración completada",
            f"META QUEST {station_number} quedó conectada por Wi-Fi.",
        )