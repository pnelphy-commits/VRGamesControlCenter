from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from services.station_manager import StationManager


class StationPreparationDialog(QDialog):
    def __init__(self, quest_controller, parent=None):
        super().__init__(parent)

        self.quest_controller = quest_controller
        self.station_manager = StationManager()
        self.station_rows = {}

        self.setWindowTitle("Preparar estaciones")
        self.setMinimumSize(650, 520)

        self.setStyleSheet("""
            QDialog {
                background-color: #080B14;
            }

            QLabel {
                color: white;
                border: none;
            }

            QFrame {
                background-color: #151A24;
                border: 1px solid #2D3748;
                border-radius: 12px;
            }

            QPushButton {
                background-color: #242B3A;
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 40px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #37415A;
            }

            QPushButton#primaryButton {
                background-color: #6C4DFF;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(16)

        title = QLabel("PREPARAR ESTACIONES")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        description = QLabel(
            "El sistema intentará conectar las Meta Quest registradas "
            "y mostrará cuáles están listas para operar."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet(
            "color: #8992A9; font-size: 14px;"
        )

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        for station_number in range(1, 5):
            row = self.create_station_row(station_number)
            main_layout.addWidget(row)

        refresh_button = QPushButton("BUSCAR Y RECONECTAR")
        refresh_button.setObjectName("primaryButton")
        refresh_button.clicked.connect(self.refresh_stations)

        close_button = QPushButton("CERRAR")
        close_button.clicked.connect(self.accept)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)

        self.quest_controller.devices_updated.connect(
            self.update_station_statuses
        )

        self.refresh_stations()

    def create_station_row(self, station_number: int) -> QFrame:
        frame = QFrame()

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)

        name_label = QLabel(f"META QUEST {station_number}")
        name_label.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )

        status_label = QLabel("BUSCANDO...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_label.setStyleSheet(
            "color: #F5B041; font-size: 14px; font-weight: bold;"
        )

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(status_label)

        self.station_rows[station_number] = status_label

        return frame

    def refresh_stations(self):
        for status_label in self.station_rows.values():
            status_label.setText("BUSCANDO...")
            status_label.setStyleSheet(
                "color: #F5B041; font-size: 14px; font-weight: bold;"
            )

        self.quest_controller.reload_stations()

    def update_station_statuses(self, devices: list):
        connected_numbers = {
            device["station_number"]
            for device in devices
            if device.get("connected")
        }

        for station_number, status_label in self.station_rows.items():
            station = self.station_manager.get_station_by_number(
                station_number
            )

            if not station:
                status_label.setText("NO CONFIGURADA")
                status_label.setStyleSheet(
                    "color: #8992A9; font-size: 14px; font-weight: bold;"
                )
                continue

            if station_number in connected_numbers:
                status_label.setText("✅ LISTA")
                status_label.setStyleSheet(
                    "color: #3DDC84; font-size: 14px; font-weight: bold;"
                )
            else:
                status_label.setText("⚠ REQUIERE CONEXIÓN")
                status_label.setStyleSheet(
                    "color: #FF5C77; font-size: 14px; font-weight: bold;"
                )