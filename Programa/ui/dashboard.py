from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from controllers.quest_controller import QuestController
from ui.quest_setup_wizard import QuestSetupWizard
from ui.station_preparation import (
    StationPreparationDialog,
)
from widgets.station_card import StationCard


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            30,
            20,
            30,
            25,
        )
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()

        title = QLabel(
            "VR GAMES CONTROL CENTER"
        )
        title.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )
        title.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            padding: 8px;
        """)

        prepare_button = QPushButton(
            "PREPARAR ESTACIONES"
        )
        prepare_button.setMinimumHeight(42)
        prepare_button.setStyleSheet("""
            QPushButton {
                background-color: #1677FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2D8CFF;
            }
        """)
        prepare_button.clicked.connect(
            self.open_station_preparation
        )

        setup_button = QPushButton(
            "CONFIGURAR META QUEST"
        )
        setup_button.setMinimumHeight(42)
        setup_button.setStyleSheet("""
            QPushButton {
                background-color: #6C4DFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #8068FF;
            }
        """)
        setup_button.clicked.connect(
            self.open_setup_wizard
        )

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(prepare_button)
        header_layout.addWidget(setup_button)

        subtitle = QLabel(
            "CONTROL DE ESTACIONES META QUEST"
        )
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        subtitle.setStyleSheet("""
            color: #8992A9;
            font-size: 15px;
            font-weight: bold;
        """)

        content_widget = QWidget()

        stations_grid = QGridLayout(
            content_widget
        )
        stations_grid.setContentsMargins(
            15,
            15,
            15,
            15,
        )
        stations_grid.setHorizontalSpacing(25)
        stations_grid.setVerticalSpacing(25)

        self.station_cards = [
            StationCard("META QUEST 1"),
            StationCard("META QUEST 2"),
            StationCard("META QUEST 3"),
            StationCard("META QUEST 4"),
        ]

        for card in self.station_cards:
            card.launch_requested.connect(
                self.launch_game
            )

            card.finish_requested.connect(
                self.finish_session
            )

        stations_grid.addWidget(
            self.station_cards[0],
            0,
            0,
        )
        stations_grid.addWidget(
            self.station_cards[1],
            0,
            1,
        )
        stations_grid.addWidget(
            self.station_cards[2],
            1,
            0,
        )
        stations_grid.addWidget(
            self.station_cards[3],
            1,
            1,
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QScrollArea.Shape.NoFrame
        )
        scroll_area.setWidget(content_widget)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(scroll_area)

        self.quest_controller = QuestController()

        self.quest_controller.devices_updated.connect(
            self.update_quest_devices
        )

    def open_station_preparation(self):
        dialog = StationPreparationDialog(
            self.quest_controller,
            self,
        )

        dialog.exec()
        self.quest_controller.refresh_devices()

    def open_setup_wizard(self):
        wizard = QuestSetupWizard(self)
        wizard.exec()

        self.quest_controller.reload_stations()

    def update_quest_devices(
        self,
        devices: list,
    ):
        for card in self.station_cards:
            card.update_device_status(False)

        for device in devices:
            station_index = (
                device["station_number"] - 1
            )

            if not (
                0 <= station_index
                < len(self.station_cards)
            ):
                continue

            self.station_cards[
                station_index
            ].update_device_status(
                connected=device["connected"],
                battery=device["battery"],
                serial=device["adb_identifier"],
                games=device.get("games", []),
            )

    def launch_game(
        self,
        card: StationCard,
        adb_identifier: str,
        component: str,
    ):
        success = (
            self.quest_controller.launch_game(
                adb_identifier,
                component,
            )
        )

        if success:
            card.begin_session()
            return

        card.launch_failed()

        QMessageBox.warning(
            self,
            "No se pudo abrir el juego",
            self.quest_controller.get_last_error()
            or (
                "Verifica que la Meta Quest esté "
                "conectada y que el juego esté instalado."
            ),
        )

    def finish_session(
        self,
        card: StationCard,
        adb_identifier: str,
    ):
        success = (
            self.quest_controller.finish_session(
                adb_identifier
            )
        )

        if success:
            card.finish_completed()
            return

        card.finish_failed()

        QMessageBox.warning(
            self,
            "No se pudo finalizar",
            self.quest_controller.get_last_error()
            or (
                "No fue posible cerrar las aplicaciones "
                "de esta Meta Quest."
            ),
        )