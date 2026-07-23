import webbrowser

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class StationCard(QFrame):
    launch_requested = Signal(object, str, str)
    finish_requested = Signal(object, str)

    def __init__(self, station_name: str):
        super().__init__()

        self.device_serial = ""
        self.device_connected = False
        self.games = []
        self.active_component = ""

        self.selected_minutes = 15
        self.remaining_seconds = self.selected_minutes * 60

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        self.setMinimumSize(380, 410)
        self.setMaximumWidth(550)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.setStyleSheet("""
            QFrame {
                background-color: #151A24;
                border: 1px solid #2D3748;
                border-radius: 16px;
            }

            QLabel {
                color: white;
                border: none;
            }

            QComboBox {
                background-color: #242B3A;
                color: white;
                border: 1px solid #37415A;
                border-radius: 8px;
                min-height: 38px;
                padding: 4px 10px;
                font-size: 14px;
                font-weight: bold;
            }

            QComboBox QAbstractItemView {
                background-color: #242B3A;
                color: white;
                selection-background-color: #6C4DFF;
            }

            QPushButton {
                background-color: #242B3A;
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 40px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #37415A;
            }

            QPushButton:disabled {
                background-color: #1B202C;
                color: #5C6373;
            }

            QPushButton#startButton {
                background-color: #6C4DFF;
            }

            QPushButton#finishButton {
                background-color: #C0392B;
            }

            QPushButton#castButton {
                background-color: #1677FF;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(11)

        title = QLabel(station_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        self.connection_label = QLabel("● DESCONECTADA")
        self.connection_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.battery_label = QLabel("🔋 --%")
        self.battery_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.session_label = QLabel()
        self.session_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.set_session_status(
            "ESTACIÓN LIBRE",
            "#8992A9",
        )

        game_label = QLabel("JUEGO")
        game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        game_label.setStyleSheet(
            "color: #8992A9; "
            "font-size: 12px; "
            "font-weight: bold;"
        )

        self.game_selector = QComboBox()
        self.game_selector.addItem(
            "Sin juegos detectados",
            "",
        )

        self.time_label = QLabel()
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.time_label.setStyleSheet(
            "font-size: 44px; "
            "font-weight: bold; "
            "color: #A98BFF;"
        )

        time_buttons_layout = QHBoxLayout()
        time_buttons_layout.setSpacing(10)

        for minutes in (10, 15, 30):
            button = QPushButton(f"{minutes} min")
            button.clicked.connect(
                lambda checked=False, value=minutes:
                self.set_session_time(value)
            )
            time_buttons_layout.addWidget(button)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.start_button = QPushButton("INICIAR")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(
            self.start_or_pause
        )

        self.finish_button = QPushButton("FINALIZAR")
        self.finish_button.setObjectName("finishButton")
        self.finish_button.clicked.connect(
            self.request_finish_session
        )

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.finish_button)

        cast_button = QPushButton("TRANSMITIR")
        cast_button.setObjectName("castButton")
        cast_button.clicked.connect(self.open_casting)

        main_layout.addWidget(title)
        main_layout.addWidget(self.connection_label)
        main_layout.addWidget(self.battery_label)
        main_layout.addWidget(self.session_label)
        main_layout.addWidget(game_label)
        main_layout.addWidget(self.game_selector)
        main_layout.addWidget(self.time_label)
        main_layout.addLayout(time_buttons_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(cast_button)

        self.update_device_status(False)
        self.refresh_time_display()

    def update_device_status(
        self,
        connected: bool,
        battery: int | None = None,
        serial: str = "",
        games: list | None = None,
    ):
        self.device_connected = connected
        self.device_serial = serial if connected else ""

        if connected:
            self.connection_label.setText("● CONECTADA")
            self.connection_label.setStyleSheet(
                "color: #3DDC84; "
                "font-size: 15px; "
                "font-weight: bold;"
            )

            self.battery_label.setText(
                f"🔋 {battery}%"
                if battery is not None
                else "🔋 --%"
            )
            self.battery_label.setStyleSheet(
                "color: #58D68D; font-size: 14px;"
            )

            self.update_games(games or [])
        else:
            self.connection_label.setText("● DESCONECTADA")
            self.connection_label.setStyleSheet(
                "color: #FF5C77; "
                "font-size: 15px; "
                "font-weight: bold;"
            )

            self.battery_label.setText("🔋 --%")
            self.battery_label.setStyleSheet(
                "color: #8992A9; font-size: 14px;"
            )

            self.update_games([])

        self.refresh_controls()

    def update_games(self, games: list):
        current_component = (
            self.game_selector.currentData()
        )

        self.games = games
        self.game_selector.blockSignals(True)
        self.game_selector.clear()

        if not games:
            self.game_selector.addItem(
                "Sin juegos detectados",
                "",
            )
        else:
            for game in games:
                self.game_selector.addItem(
                    game["name"],
                    game["component"],
                )

            if current_component:
                index = self.game_selector.findData(
                    current_component
                )

                if index >= 0:
                    self.game_selector.setCurrentIndex(
                        index
                    )

        self.game_selector.blockSignals(False)

    def refresh_controls(self):
        has_games = bool(self.games)

        self.game_selector.setEnabled(
            self.device_connected and has_games
        )

        if self.start_button.text() != "ABRIENDO...":
            self.start_button.setEnabled(
                self.device_connected and has_games
            )

        if self.finish_button.text() != "FINALIZANDO...":
            self.finish_button.setEnabled(
                self.device_connected
            )

    def start_or_pause(self):
        if not self.device_connected:
            return

        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("CONTINUAR")
            self.set_session_status(
                "SESIÓN PAUSADA",
                "#F5B041",
            )
            return

        if self.start_button.text() == "CONTINUAR":
            self.begin_session()
            return

        component = self.game_selector.currentData()

        if not component:
            return

        self.active_component = component

        self.start_button.setEnabled(False)
        self.start_button.setText("ABRIENDO...")

        self.launch_requested.emit(
            self,
            self.device_serial,
            component,
        )

    def begin_session(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = (
                self.selected_minutes * 60
            )

        self.timer.start()
        self.start_button.setEnabled(True)
        self.start_button.setText("PAUSAR")

        self.set_session_status(
            "SESIÓN EN CURSO",
            "#FF5C77",
        )

    def launch_failed(self):
        self.active_component = ""
        self.start_button.setEnabled(True)
        self.start_button.setText("INICIAR")

        self.set_session_status(
            "ERROR AL ABRIR JUEGO",
            "#FF5C77",
        )

    def request_finish_session(self):
        if not self.device_connected:
            return

        self.timer.stop()

        self.start_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        self.finish_button.setText("FINALIZANDO...")

        self.set_session_status(
            "CERRANDO APLICACIONES...",
            "#F5B041",
        )

        self.finish_requested.emit(
            self,
            self.device_serial,
        )

    def finish_completed(self):
        self.active_component = ""
        self.remaining_seconds = (
            self.selected_minutes * 60
        )

        self.start_button.setText("INICIAR")
        self.finish_button.setText("FINALIZAR")

        self.set_session_status(
            "ESTACIÓN LIBRE",
            "#8992A9",
        )

        self.refresh_time_display()
        self.refresh_controls()

    def finish_failed(self):
        self.start_button.setText("INICIAR")
        self.finish_button.setText("FINALIZAR")

        self.set_session_status(
            "ERROR AL FINALIZAR",
            "#FF5C77",
        )

        self.refresh_controls()

    def set_session_time(self, minutes: int):
        self.timer.stop()
        self.selected_minutes = minutes
        self.remaining_seconds = minutes * 60
        self.active_component = ""

        self.start_button.setText("INICIAR")

        self.set_session_status(
            "ESTACIÓN LIBRE",
            "#8992A9",
        )

        self.refresh_time_display()
        self.refresh_controls()

    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.refresh_time_display()

        if self.remaining_seconds == 0:
            self.timer.stop()
            self.start_button.setText("INICIAR")

            self.set_session_status(
                "TIEMPO FINALIZADO",
                "#FF5C77",
            )

            self.refresh_controls()
            QApplication.beep()

    def refresh_time_display(self):
        minutes, seconds = divmod(
            self.remaining_seconds,
            60,
        )

        self.time_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

    def set_session_status(
        self,
        text: str,
        color: str,
    ):
        self.session_label.setText(text)
        self.session_label.setStyleSheet(
            f"color: {color}; "
            "font-size: 13px; "
            "font-weight: bold;"
        )

    def open_casting(self):
        webbrowser.open(
            "https://horizon.meta.com/casting"
        )