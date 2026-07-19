from PySide6.QtWidgets import QMainWindow

from ui.dashboard import Dashboard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VR GAMES CONTROL CENTER")
        self.resize(1100, 850)
        self.setMinimumSize(950, 750)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #080B14;
            }
        """)

        dashboard = Dashboard()
        self.setCentralWidget(dashboard)