from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from widgets.station_card import StationCard


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 25)
        main_layout.setSpacing(15)

        title = QLabel("VR GAMES CONTROL CENTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            padding: 8px;
        """)

        subtitle = QLabel("CONTROL DE ESTACIONES META QUEST")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #8992A9;
            font-size: 15px;
            font-weight: bold;
        """)

        content_widget = QWidget()

        stations_grid = QGridLayout(content_widget)
        stations_grid.setContentsMargins(15, 15, 15, 15)
        stations_grid.setHorizontalSpacing(25)
        stations_grid.setVerticalSpacing(25)

        stations_grid.setColumnStretch(0, 1)
        stations_grid.setColumnStretch(1, 1)
        stations_grid.setRowStretch(0, 1)
        stations_grid.setRowStretch(1, 1)

        station_1 = StationCard("META QUEST 1")
        station_2 = StationCard("META QUEST 2")
        station_3 = StationCard("META QUEST 3")
        station_4 = StationCard("META QUEST 4")

        stations_grid.addWidget(
            station_1,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        stations_grid.addWidget(
            station_2,
            0,
            1,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        stations_grid.addWidget(
            station_3,
            1,
            0,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        stations_grid.addWidget(
            station_4,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(content_widget)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #10141E;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #6C4DFF;
                border-radius: 6px;
                min-height: 30px;
            }
        """)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(scroll_area)