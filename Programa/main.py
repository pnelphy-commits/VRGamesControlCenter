import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


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


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())