import webbrowser

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class StationCard(QFrame):
    def __init__(self, station_name: str):
        super().__init__()

        self.selected_minutes = 15
        self.remaining_seconds = self.selected_minutes * 60

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        self.setMinimumSize(380, 350)
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

            QPushButton#startButton {
                background-color: #6C4DFF;
            }

            QPushButton#startButton:hover {
                background-color: #8068FF;
            }

            QPushButton#resetButton {
                background-color: #C0392B;
            }

            QPushButton#resetButton:hover {
                background-color: #D64A3A;
            }

            QPushButton#castButton {
                background-color: #1677FF;
            }

            QPushButton#castButton:hover {
                background-color: #3389FF;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(12)

        title = QLabel(station_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        self.status_label = QLabel("● LIBRE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #3DDC84; font-size: 15px; font-weight: bold;"
        )

        self.battery_label = QLabel("🔋 100%")
        self.battery_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battery_label.setStyleSheet(
            "color: #58D68D; font-size: 14px;"
        )

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(
            "font-size: 44px; font-weight: bold; color: #A98BFF;"
        )

        time_buttons_layout = QHBoxLayout()
        time_buttons_layout.setSpacing(10)

        for minutes in (10, 15, 30):
            button = QPushButton(f"{minutes} min")
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            button.clicked.connect(
                lambda checked=False, value=minutes:
                self.set_session_time(value)
            )
            time_buttons_layout.addWidget(button)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.start_button = QPushButton("INICIAR")
        self.start_button.setObjectName("startButton")
        self.start_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.start_button.clicked.connect(self.start_or_pause)

        reset_button = QPushButton("REINICIAR")
        reset_button.setObjectName("resetButton")
        reset_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        reset_button.clicked.connect(self.reset_session)

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(reset_button)

        cast_button = QPushButton("TRANSMITIR")
        cast_button.setObjectName("castButton")
        cast_button.clicked.connect(self.open_casting)

        main_layout.addWidget(title)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.battery_label)
        main_layout.addWidget(self.time_label)
        main_layout.addLayout(time_buttons_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(cast_button)

        self.refresh_time_display()

    def open_casting(self):
        webbrowser.open("https://horizon.meta.com/casting")

    def set_session_time(self, minutes: int):
        self.timer.stop()
        self.selected_minutes = minutes
        self.remaining_seconds = minutes * 60
        self.start_button.setText("INICIAR")
        self.set_status("LIBRE", "#3DDC84")
        self.refresh_time_display()

    def start_or_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("CONTINUAR")
            self.set_status("PAUSADO", "#F5B041")
            return

        if self.remaining_seconds <= 0:
            self.reset_session()

        self.timer.start()
        self.start_button.setText("PAUSAR")
        self.set_status("EN USO", "#FF5C77")

    def reset_session(self):
        self.timer.stop()
        self.remaining_seconds = self.selected_minutes * 60
        self.start_button.setText("INICIAR")
        self.set_status("LIBRE", "#3DDC84")
        self.refresh_time_display()

    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.refresh_time_display()

        if self.remaining_seconds == 0:
            self.timer.stop()
            self.start_button.setText("INICIAR")
            self.set_status("TIEMPO FINALIZADO", "#FF5C77")
            QApplication.beep()

    def refresh_time_display(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def set_status(self, text: str, color: str):
        self.status_label.setText(f"● {text}")
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 15px; font-weight: bold;"
        )