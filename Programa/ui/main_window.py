from PySide6.QtWidgets import QMainWindow

from ui.dashboard import Dashboard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "VR GAMES CONTROL CENTER"
        )

        self.setMinimumSize(1100, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #080B14;
            }
        """)

        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)

    def closeEvent(self, event):
        self.dashboard.quest_controller.shutdown()
        event.accept()