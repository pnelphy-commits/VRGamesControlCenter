from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.theme import COLORS


class MetricWidget(QWidget):
    def __init__(
        self,
        icon: str,
        value: str,
        description: str,
        accent_color: str,
    ):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"""
            color: {accent_color};
            font-size: 26px;
            font-weight: bold;
            """
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 21px;
            font-weight: bold;
            """
        )

        self.description_label = QLabel(description)
        self.description_label.setStyleSheet(
            f"""
            color: {accent_color};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
            """
        )

        text_layout.addWidget(self.value_label)
        text_layout.addWidget(self.description_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)

    def set_value(self, value: str):
        self.value_label.setText(value)

    def set_description(self, description: str):
        self.description_label.setText(description)


class TopBar(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("topBar")
        self.setMinimumHeight(92)

        self.setStyleSheet(
            f"""
            QFrame#topBar {{
                background-color: {COLORS["panel"]};
                border: 1px solid {COLORS["blue_dark"]};
                border-radius: 14px;
            }}
            """
        )

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(22, 10, 22, 10)
        main_layout.setSpacing(10)

        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(14)

        logo_text = QLabel("VR")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setFixedSize(64, 54)
        logo_text.setStyleSheet(
            f"""
            color: {COLORS["blue"]};
            background-color: #080D18;
            border: 1px solid {COLORS["magenta"]};
            border-radius: 12px;
            font-size: 25px;
            font-weight: bold;
            """
        )

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)

        title = QLabel("VR GAMES")
        title.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 23px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        subtitle = QLabel("CONTROL CENTER")
        subtitle.setStyleSheet(
            f"""
            color: {COLORS["muted"]};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 4px;
            """
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        brand_layout.addWidget(logo_text)
        brand_layout.addLayout(title_layout)

        self.online_metric = MetricWidget(
            "🥽",
            "0 / 4",
            "META ONLINE",
            COLORS["green"],
        )

        self.games_metric = MetricWidget(
            "🎮",
            "0",
            "JUEGOS",
            COLORS["blue"],
        )

        self.battery_metric = MetricWidget(
            "🔋",
            "--%",
            "BATERÍA PROMEDIO",
            COLORS["green"],
        )

        self.date_metric = MetricWidget(
            "📅",
            "",
            "",
            COLORS["blue"],
        )

        main_layout.addLayout(brand_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.online_metric)
        main_layout.addWidget(self.games_metric)
        main_layout.addWidget(self.battery_metric)
        main_layout.addWidget(self.date_metric)

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start()

        self.update_clock()

    def update_clock(self):
        now = datetime.now()

        self.date_metric.set_value(
            now.strftime("%d %b %Y").upper()
        )

        self.date_metric.set_description(
            now.strftime("%A · %I:%M:%S %p").upper()
        )

    def update_metrics(self, devices: list):
        connected_devices = [
            device
            for device in devices
            if device.get("connected")
        ]

        online_count = len(connected_devices)

        self.online_metric.set_value(
            f"{online_count} / 4"
        )

        all_games = set()

        for device in connected_devices:
            for game in device.get("games", []):
                component = game.get("component")

                if component:
                    all_games.add(component)

        self.games_metric.set_value(
            str(len(all_games))
        )

        batteries = [
            device.get("battery")
            for device in connected_devices
            if device.get("battery") is not None
        ]

        if batteries:
            average_battery = round(
                sum(batteries) / len(batteries)
            )

            self.battery_metric.set_value(
                f"{average_battery}%"
            )
        else:
            self.battery_metric.set_value("--%")