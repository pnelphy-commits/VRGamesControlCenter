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


class CastDialog(QDialog):
    def __init__(
        self,
        station_number: int,
        station_name: str,
        adb_identifier: str = "",
        parent=None,
    ):
        super().__init__(parent)

        self.station_number = station_number
        self.station_name = station_name
        self.adb_identifier = adb_identifier

        self.display_manager = DisplayManager()

        self.setWindowTitle(
            f"Transmitir {self.station_name}"
        )

        self.setMinimumSize(620, 620)
        self.setModal(True)

        self.build_interface()
        self.load_displays()
        self.update_quest_status()

    def build_interface(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        main_layout.setSpacing(16)

        title = QLabel(
            "MÓDULO DE TRANSMISIÓN"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            """
            color: #00A8FF;
            font-size: 22px;
            font-weight: bold;
            """
        )

        station_label = QLabel(
            f"Estación: {self.station_name}"
        )

        station_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        station_label.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 17px;
            font-weight: bold;
            """
        )

        self.quest_status_label = QLabel()

        self.quest_status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        configuration_frame = QFrame()

        configuration_frame.setStyleSheet(
            """
            QFrame {
                background-color: #0C1426;
                border: 1px solid #163A70;
                border-radius: 10px;
            }

            QLabel {
                border: none;
            }

            QLineEdit {
                min-height: 38px;
                padding: 4px 10px;
                color: #FFFFFF;
                background-color: #080D18;
                border: 1px solid #1F5D99;
                border-radius: 7px;
            }

            QLineEdit:focus {
                border: 1px solid #00A8FF;
            }
            """
        )

        configuration_layout = QVBoxLayout(
            configuration_frame
        )

        configuration_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        configuration_layout.setSpacing(12)

        select_label = QLabel(
            "Selecciona el televisor:"
        )

        select_label.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
            """
        )

        self.display_combo = QComboBox()

        self.display_combo.currentIndexChanged.connect(
            self.display_selected
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.device_name_input = QLineEdit()

        self.device_name_input.setPlaceholderText(
            "Ejemplo: Vizio Chromecast"
        )

        self.ip_input = QLineEdit()

        self.ip_input.setPlaceholderText(
            "Ejemplo: 10.0.0.219"
        )

        form_layout.addRow(
            "Nombre del dispositivo:",
            self.device_name_input,
        )

        form_layout.addRow(
            "Dirección IP:",
            self.ip_input,
        )

        self.display_status_label = QLabel(
            "TV SIN CONFIGURAR"
        )

        self.display_status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.display_status_label.setStyleSheet(
            """
            color: #F6C945;
            font-size: 13px;
            font-weight: bold;
            """
        )

        configuration_layout.addWidget(
            select_label
        )

        configuration_layout.addWidget(
            self.display_combo
        )

        configuration_layout.addLayout(
            form_layout
        )

        configuration_layout.addWidget(
            self.display_status_label
        )

        configuration_buttons = QHBoxLayout()
        configuration_buttons.setSpacing(10)

        self.save_device_button = QPushButton(
            "GUARDAR TV"
        )

        self.save_device_button.setProperty(
            "buttonType",
            "success",
        )

        self.save_device_button.clicked.connect(
            self.save_display_configuration
        )

        self.assign_button = QPushButton(
            "ASIGNAR A ESTA META"
        )

        self.assign_button.setProperty(
            "buttonType",
            "primary",
        )

        self.assign_button.clicked.connect(
            self.assign_display
        )

        configuration_buttons.addWidget(
            self.save_device_button
        )

        configuration_buttons.addWidget(
            self.assign_button
        )

        information_label = QLabel(
            "La Meta Quest debe conectarse directamente "
            "al receptor Chromecast del televisor.\n\n"
            "Para esta estación, abre la opción Transmitir "
            "en la Meta Quest y selecciona el nombre del "
            "televisor asignado.\n\n"
            "El botón PROBAR CONEXIÓN comprueba si la TV "
            "está disponible en la red."
        )

        information_label.setWordWrap(True)

        information_label.setStyleSheet(
            """
            color: #C7D3E8;
            background-color: #080D18;
            border: 1px solid #1F5D99;
            border-radius: 10px;
            padding: 14px;
            """
        )

        action_buttons = QHBoxLayout()
        action_buttons.setSpacing(10)

        close_button = QPushButton(
            "CERRAR"
        )

        close_button.clicked.connect(
            self.reject
        )

        self.test_connection_button = QPushButton(
            "PROBAR CONEXIÓN"
        )

        self.test_connection_button.setProperty(
            "buttonType",
            "success",
        )

        self.test_connection_button.clicked.connect(
            self.test_display_connection
        )

        self.start_cast_button = QPushButton(
            "INICIAR TRANSMISIÓN"
        )

        self.start_cast_button.setProperty(
            "buttonType",
            "danger",
        )

        self.start_cast_button.clicked.connect(
            self.start_casting
        )

        action_buttons.addWidget(
            close_button
        )

        action_buttons.addStretch()

        action_buttons.addWidget(
            self.test_connection_button
        )

        action_buttons.addWidget(
            self.start_cast_button
        )

        main_layout.addWidget(title)
        main_layout.addWidget(station_label)

        main_layout.addWidget(
            self.quest_status_label
        )

        main_layout.addWidget(
            configuration_frame
        )

        main_layout.addLayout(
            configuration_buttons
        )

        main_layout.addWidget(
            information_label
        )

        main_layout.addLayout(
            action_buttons
        )

    def update_quest_status(self):
        if self.adb_identifier:
            self.quest_status_label.setText(
                f"● META CONECTADA: "
                f"{self.adb_identifier}"
            )

            self.quest_status_label.setStyleSheet(
                """
                color: #25F29A;
                font-size: 13px;
                font-weight: bold;
                """
            )

        else:
            self.quest_status_label.setText(
                "● META NO DETECTADA"
            )

            self.quest_status_label.setStyleSheet(
                """
                color: #FF4E6D;
                font-size: 13px;
                font-weight: bold;
                """
            )

    def load_displays(self):
        self.display_manager.reload()
        self.display_combo.clear()

        selected_index = 0

        for index, display in enumerate(
            self.display_manager.displays
        ):
            display_number = display.get(
                "display_number"
            )

            display_name = display.get(
                "name",
                f"TV META {display_number}",
            )

            device_name = display.get(
                "device_name",
                "",
            )

            combo_text = display_name

            if device_name:
                combo_text = (
                    f"{display_name} - {device_name}"
                )

            self.display_combo.addItem(
                combo_text,
                display_number,
            )

            if (
                display.get("assigned_station")
                == self.station_number
            ):
                selected_index = index

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

            self.display_status_label.setText(
                "● TV NO ENCONTRADA"
            )

            self.display_status_label.setStyleSheet(
                """
                color: #FF4E6D;
                font-size: 13px;
                font-weight: bold;
                """
            )

            self.test_connection_button.setEnabled(
                False
            )

            self.start_cast_button.setEnabled(
                False
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

        configured = (
            self.display_manager.is_display_configured(
                display
            )
        )

        if configured:
            status_text = "● TV CONFIGURADA"

            if assigned_station:
                status_text += (
                    f" · META QUEST "
                    f"{assigned_station}"
                )

            self.display_status_label.setText(
                status_text
            )

            self.display_status_label.setStyleSheet(
                """
                color: #25F29A;
                font-size: 13px;
                font-weight: bold;
                """
            )

        else:
            self.display_status_label.setText(
                "● TV SIN CONFIGURAR"
            )

            self.display_status_label.setStyleSheet(
                """
                color: #F6C945;
                font-size: 13px;
                font-weight: bold;
                """
            )

        self.test_connection_button.setEnabled(
            configured
        )

        self.start_cast_button.setEnabled(
            configured
        )

    def save_display_configuration(self):
        display_number = (
            self.display_combo.currentData()
        )

        if display_number is None:
            QMessageBox.warning(
                self,
                "Sin televisor",
                "Selecciona un televisor.",
            )
            return

        success, message = (
            self.display_manager.update_display(
                display_number=display_number,
                device_name=(
                    self.device_name_input.text()
                ),
                ip_address=(
                    self.ip_input.text()
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
            "Configuración guardada",
            message,
        )

        self.load_displays()

    def assign_display(self):
        display_number = (
            self.display_combo.currentData()
        )

        if display_number is None:
            QMessageBox.warning(
                self,
                "Sin televisor",
                "Selecciona un televisor.",
            )
            return

        success, message = (
            self.display_manager.assign_display_to_station(
                display_number=display_number,
                station_number=self.station_number,
            )
        )

        if not success:
            QMessageBox.warning(
                self,
                "No se pudo asignar",
                message,
            )
            return

        QMessageBox.information(
            self,
            "Asignación guardada",
            message,
        )

        self.load_displays()

    def test_display_connection(self):
        display_number = (
            self.display_combo.currentData()
        )

        display = (
            self.display_manager.get_display_by_number(
                display_number
            )
        )

        if not display:
            QMessageBox.warning(
                self,
                "TV no encontrada",
                (
                    "No se encontró el televisor "
                    "seleccionado."
                ),
            )
            return

        ip_address = (
            display.get("ip", "").strip()
        )

        if not ip_address:
            QMessageBox.warning(
                self,
                "Sin dirección IP",
                (
                    "Primero debes guardar la "
                    "dirección IP del televisor."
                ),
            )
            return

        self.test_connection_button.setEnabled(
            False
        )

        self.test_connection_button.setText(
            "PROBANDO..."
        )

        success, message = (
            NetworkService.ping_device(
                ip_address
            )
        )

        self.test_connection_button.setText(
            "PROBAR CONEXIÓN"
        )

        self.test_connection_button.setEnabled(
            True
        )

        if success:
            self.display_status_label.setText(
                "● TV EN LÍNEA"
            )

            self.display_status_label.setStyleSheet(
                """
                color: #25F29A;
                font-size: 13px;
                font-weight: bold;
                """
            )

            QMessageBox.information(
                self,
                "Conexión correcta",
                message,
            )

        else:
            self.display_status_label.setText(
                "● TV SIN RESPUESTA"
            )

            self.display_status_label.setStyleSheet(
                """
                color: #FF4E6D;
                font-size: 13px;
                font-weight: bold;
                """
            )

            QMessageBox.warning(
                self,
                "Sin conexión",
                message,
            )

    def start_casting(self):
        display_number = (
            self.display_combo.currentData()
        )

        display = (
            self.display_manager.get_display_by_number(
                display_number
            )
        )

        if not display:
            QMessageBox.warning(
                self,
                "TV no encontrada",
                "No se encontró el televisor.",
            )
            return

        if not self.display_manager.is_display_configured(
            display
        ):
            QMessageBox.warning(
                self,
                "TV sin configurar",
                (
                    "Primero guarda el nombre y "
                    "la dirección IP del televisor."
                ),
            )
            return

        if not self.adb_identifier:
            QMessageBox.warning(
                self,
                "Meta desconectada",
                (
                    "La TV está configurada, pero "
                    "la Meta Quest no está conectada."
                ),
            )
            return

        device_name = display.get(
            "device_name",
            "Vizio Chromecast",
        )

        QMessageBox.information(
            self,
            "Iniciar transmisión",
            (
                f"Estación: {self.station_name}\n"
                f"Meta: {self.adb_identifier}\n"
                f"TV: {device_name}\n"
                f"IP: {display.get('ip')}\n\n"
                "Ponte la Meta Quest y entra en:\n\n"
                "Cámara → Transmitir\n\n"
                f"Selecciona: {device_name}"
            ),
        )