from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from services.display_manager import DisplayManager
from services.network_service import NetworkService


class TvSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.display_manager = DisplayManager()

        self.setWindowTitle(
            "Configurar TVs"
        )

        self.setMinimumSize(
            650,
            610,
        )

        self.setModal(True)

        self.build_interface()
        self.load_displays()

    def build_interface(self):
        self.setStyleSheet(
            """
            QDialog {
                background-color: #080D18;
            }

            QLabel {
                color: #FFFFFF;
            }

            QComboBox,
            QLineEdit {
                min-height: 40px;
                padding: 4px 10px;
                color: #FFFFFF;
                background-color: #111A2E;
                border: 1px solid #1F5D99;
                border-radius: 8px;
                font-size: 14px;
            }

            QComboBox:focus,
            QLineEdit:focus {
                border: 1px solid #00A8FF;
            }

            QPushButton {
                min-height: 42px;
                padding: 6px 14px;
                color: #FFFFFF;
                background-color: #242B3A;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #37415A;
            }

            QPushButton#saveButton {
                background-color: #1677FF;
            }

            QPushButton#saveButton:hover {
                background-color: #3190FF;
            }

            QPushButton#testButton {
                background-color: #198754;
            }

            QPushButton#testButton:hover {
                background-color: #20A867;
            }

            QPushButton#deleteButton {
                background-color: #B33939;
            }

            QPushButton#deleteButton:hover {
                background-color: #D64545;
            }
            """
        )

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            26,
            24,
            26,
            24,
        )

        main_layout.setSpacing(16)

        title = QLabel(
            "CONFIGURAR TVs"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            """
            color: #00A8FF;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        subtitle = QLabel(
            (
                "Agrega, reemplaza, mueve o asigna "
                "cada televisor a una Meta Quest."
            )
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle.setWordWrap(True)

        subtitle.setStyleSheet(
            """
            color: #9AA8C1;
            font-size: 13px;
            """
        )

        configuration_frame = QFrame()

        configuration_frame.setStyleSheet(
            """
            QFrame {
                background-color: #0C1426;
                border: 1px solid #163A70;
                border-radius: 12px;
            }

            QLabel {
                border: none;
            }
            """
        )

        frame_layout = QVBoxLayout(
            configuration_frame
        )

        frame_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        frame_layout.setSpacing(15)

        form_layout = QFormLayout()

        form_layout.setHorizontalSpacing(
            20
        )

        form_layout.setVerticalSpacing(
            15
        )

        self.display_combo = QComboBox()

        self.display_combo.currentIndexChanged.connect(
            self.display_selected
        )

        self.device_name_input = QLineEdit()

        self.device_name_input.setPlaceholderText(
            "Ejemplo: Meta 01"
        )

        self.ip_input = QLineEdit()

        self.ip_input.setPlaceholderText(
            "Ejemplo: 10.0.0.219"
        )

        self.station_combo = QComboBox()

        for station_number in range(
            1,
            5,
        ):
            self.station_combo.addItem(
                (
                    f"META QUEST "
                    f"{station_number}"
                ),
                station_number,
            )

        form_layout.addRow(
            "TV:",
            self.display_combo,
        )

        form_layout.addRow(
            "Nombre Chromecast:",
            self.device_name_input,
        )

        form_layout.addRow(
            "Dirección IP:",
            self.ip_input,
        )

        form_layout.addRow(
            "Asignar a:",
            self.station_combo,
        )

        self.status_label = QLabel(
            "● SIN CONFIGURAR"
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setStyleSheet(
            """
            color: #F6C945;
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
            """
        )

        frame_layout.addLayout(
            form_layout
        )

        frame_layout.addWidget(
            self.status_label
        )

        instructions = QLabel(
            (
                "El nombre Chromecast debe ser exactamente "
                "igual al que aparece dentro de la Meta Quest.\n\n"
                "Ejemplo: si dentro del visor aparece “Meta 01”, "
                "escribe solamente “Meta 01”."
            )
        )

        instructions.setWordWrap(True)

        instructions.setStyleSheet(
            """
            color: #C7D3E8;
            background-color: #10192C;
            border: 1px solid #1F5D99;
            border-radius: 10px;
            padding: 14px;
            """
        )

        management_buttons = QHBoxLayout()

        management_buttons.setSpacing(
            10
        )

        self.test_button = QPushButton(
            "PROBAR CONEXIÓN"
        )

        self.test_button.setObjectName(
            "testButton"
        )

        self.test_button.clicked.connect(
            self.test_connection
        )

        self.save_button = QPushButton(
            "GUARDAR Y ASIGNAR"
        )

        self.save_button.setObjectName(
            "saveButton"
        )

        self.save_button.clicked.connect(
            self.save_configuration
        )

        self.delete_button = QPushButton(
            "QUITAR TV"
        )

        self.delete_button.setObjectName(
            "deleteButton"
        )

        self.delete_button.clicked.connect(
            self.clear_configuration
        )

        management_buttons.addWidget(
            self.test_button
        )

        management_buttons.addWidget(
            self.save_button
        )

        management_buttons.addWidget(
            self.delete_button
        )

        close_layout = QHBoxLayout()

        close_button = QPushButton(
            "CERRAR"
        )

        close_button.clicked.connect(
            self.accept
        )

        close_layout.addStretch()

        close_layout.addWidget(
            close_button
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        main_layout.addWidget(
            configuration_frame
        )

        main_layout.addWidget(
            instructions
        )

        main_layout.addLayout(
            management_buttons
        )

        main_layout.addStretch()

        main_layout.addLayout(
            close_layout
        )

    def load_displays(
        self,
        selected_display_number: int | None = None,
    ):
        self.display_manager.reload()

        self.display_combo.blockSignals(
            True
        )

        self.display_combo.clear()

        selected_index = 0

        for index, display in enumerate(
            self.display_manager.displays
        ):
            display_number = display.get(
                "display_number"
            )

            device_name = display.get(
                "device_name",
                "",
            )

            combo_text = (
                f"TV META {display_number}"
            )

            if device_name:
                combo_text += (
                    f" — {device_name}"
                )

            self.display_combo.addItem(
                combo_text,
                display_number,
            )

            if (
                selected_display_number
                == display_number
            ):
                selected_index = index

        self.display_combo.blockSignals(
            False
        )

        if self.display_combo.count() > 0:
            self.display_combo.setCurrentIndex(
                selected_index
            )

        self.display_selected()

    def display_selected(self):
        display_number = (
            self.display_combo.currentData()
        )

        display = (
            self.display_manager.get_display_by_number(
                display_number
            )
        )

        if not display:
            self.device_name_input.clear()
            self.ip_input.clear()

            self.status_label.setText(
                "● TV NO ENCONTRADA"
            )

            self.status_label.setStyleSheet(
                """
                color: #FF4E6D;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                """
            )

            return

        self.device_name_input.setText(
            display.get(
                "device_name",
                "",
            )
        )

        self.ip_input.setText(
            display.get(
                "ip",
                "",
            )
        )

        assigned_station = display.get(
            "assigned_station"
        )

        if assigned_station in (
            1,
            2,
            3,
            4,
        ):
            station_index = (
                self.station_combo.findData(
                    assigned_station
                )
            )

            if station_index >= 0:
                self.station_combo.setCurrentIndex(
                    station_index
                )

        if (
            self.display_manager.is_display_configured(
                display
            )
        ):
            self.status_label.setText(
                (
                    "● CONFIGURADA · "
                    f"META QUEST {assigned_station}"
                )
            )

            self.status_label.setStyleSheet(
                """
                color: #25F29A;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                """
            )

        else:
            self.status_label.setText(
                "● SIN CONFIGURAR"
            )

            self.status_label.setStyleSheet(
                """
                color: #F6C945;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                """
            )

    def save_configuration(self):
        display_number = (
            self.display_combo.currentData()
        )

        station_number = (
            self.station_combo.currentData()
        )

        success, message = (
            self.display_manager.save_display_configuration(
                display_number=display_number,
                device_name=(
                    self.device_name_input.text()
                ),
                ip_address=(
                    self.ip_input.text()
                ),
                assigned_station=(
                    station_number
                ),
            )
        )

        if not success:
            QMessageBox.warning(
                self,
                "No se pudo guardar",
                message,
            )
            return

        QMessageBox.information(
            self,
            "TV configurada",
            message,
        )

        self.load_displays(
            selected_display_number=(
                display_number
            )
        )

    def test_connection(self):
        ip_address = (
            self.ip_input.text().strip()
        )

        valid_ip, message = (
            self.display_manager.validate_ip(
                ip_address
            )
        )

        if not valid_ip:
            QMessageBox.warning(
                self,
                "Dirección IP incorrecta",
                message,
            )
            return

        self.test_button.setEnabled(
            False
        )

        self.test_button.setText(
            "PROBANDO..."
        )

        online, network_message = (
            NetworkService.ping_device(
                ip_address,
                timeout_seconds=2,
            )
        )

        self.test_button.setText(
            "PROBAR CONEXIÓN"
        )

        self.test_button.setEnabled(
            True
        )

        if online:
            self.status_label.setText(
                "● TV EN LÍNEA"
            )

            self.status_label.setStyleSheet(
                """
                color: #25F29A;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                """
            )

            QMessageBox.information(
                self,
                "Conexión correcta",
                network_message,
            )

        else:
            self.status_label.setText(
                "● TV SIN RESPUESTA"
            )

            self.status_label.setStyleSheet(
                """
                color: #FF4E6D;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                """
            )

            QMessageBox.warning(
                self,
                "Sin conexión",
                network_message,
            )

    def clear_configuration(self):
        display_number = (
            self.display_combo.currentData()
        )

        confirmation = QMessageBox.question(
            self,
            "Quitar configuración",
            (
                f"¿Deseas quitar la configuración "
                f"de TV META {display_number}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            confirmation
            != QMessageBox.StandardButton.Yes
        ):
            return

        success, message = (
            self.display_manager.clear_display(
                display_number
            )
        )

        if not success:
            QMessageBox.warning(
                self,
                "No se pudo quitar",
                message,
            )
            return

        QMessageBox.information(
            self,
            "TV eliminada",
            message,
        )

        self.load_displays(
            selected_display_number=(
                display_number
            )
        )