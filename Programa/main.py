import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from ui.theme import APP_STYLE


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(
        "VR Games Control Center"
    )

    app.setOrganizationName(
        "VR Games Bávaro"
    )

    app.setStyleSheet(APP_STYLE)

    main_window = None
    splash_screen = None

    def open_main_window():
        nonlocal main_window

        main_window = MainWindow()
        main_window.showMaximized()

    splash_screen = SplashScreen(
        on_finished=open_main_window
    )

    splash_screen.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()