from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QGridLayout,
)

from widgets.station_card import StationCard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VR GAMES CONTROL CENTER")
        self.resize(1200, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #080B14;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("VR GAMES CONTROL CENTER")

        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        grid = QGridLayout()

        grid.addWidget(StationCard("🥽 META QUEST 1"), 0, 0)
        grid.addWidget(StationCard("🥽 META QUEST 2"), 0, 1)
        grid.addWidget(StationCard("🥽 META QUEST 3"), 1, 0)
        grid.addWidget(StationCard("🥽 META QUEST 4"), 1, 1)

        layout.addLayout(grid)
        layout.addStretch()