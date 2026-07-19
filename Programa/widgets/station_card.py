from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class StationCard(QFrame):
    def __init__(self, title):
        super().__init__()

        self.setFixedSize(250, 180)

        self.setStyleSheet("""
            QFrame {
                background-color: #151A24;
                border: 2px solid #2D3748;
                border-radius: 12px;
            }

            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)