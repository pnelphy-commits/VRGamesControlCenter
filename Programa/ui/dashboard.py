from PySide6.QtCore import (
    QObject,
    QThread,
    Qt,
    Signal,
    Slot,
)
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
from services.cast_service import CastService
from services.display_manager import DisplayManager
from services.network_service import NetworkService
from ui.quest_setup_wizard import QuestSetupWizard
from ui.station_preparation import StationPreparationDialog
from ui.tv_setup_dialog import TvSetupDialog
from widgets.station_card import StationCard
from widgets.top_bar import TopBar


class CastWorker(QObject):
    finished = Signal(
        bool,
        str,
        object,
    )

    def __init__(
        self,
        card: StationCard,
        adb_identifier: str,
        receiver_name: str,
        television_ip: str,
    ):
        super().__init__()

        self.card = card
        self.adb_identifier = adb_identifier
        self.receiver_name = receiver_name
        self.television_ip = television_ip

    @Slot()
    def run(self):
        if self.television_ip:
            online, message = (
                NetworkService.ping_device(
                    self.television_ip,
                    timeout_seconds=2,
                )
            )

            if not online:
                self.finished.emit(
                    False,
                    (
                        "La televisión no respondió "
                        "en la red.\n\n"
                        f"{message}"
                    ),
                    self.card,
                )
                return

        cast_service = CastService()

        success, message = (
            cast_service.start_casting(
                device_identifier=(
                    self.adb_identifier
                ),
                receiver_name=(
                    self.receiver_name
                ),
            )
        )

        self.finished.emit(
            success,
            message,
            self.card,
        )


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.cast_threads = {}

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            16,
            20,
            18,
        )

        main_layout.setSpacing(14)

        self.top_bar = TopBar()

        actions_layout = QHBoxLayout()

        actions_layout.setSpacing(
            10
        )

        section_title = QLabel(
            "ESTACIONES META QUEST"
        )

        section_title.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        prepare_button = QPushButton(
            "PREPARAR ESTACIONES"
        )

        prepare_button.setProperty(
            "buttonType",
            "primary",
        )

        prepare_button.clicked.connect(
            self.open_station_preparation
        )

        setup_quest_button = QPushButton(
            "CONFIGURAR META QUEST"
        )

        setup_quest_button.setProperty(
            "buttonType",
            "danger",
        )

        setup_quest_button.clicked.connect(
            self.open_setup_wizard
        )

        setup_tv_button = QPushButton(
            "CONFIGURAR TVs"
        )

        setup_tv_button.setProperty(
            "buttonType",
            "success",
        )

        setup_tv_button.clicked.connect(
            self.open_tv_setup
        )

        actions_layout.addWidget(
            section_title
        )

        actions_layout.addStretch()

        actions_layout.addWidget(
            prepare_button
        )

        actions_layout.addWidget(
            setup_quest_button
        )

        actions_layout.addWidget(
            setup_tv_button
        )

        content_widget = QWidget()

        stations_grid = QGridLayout(
            content_widget
        )

        stations_grid.setContentsMargins(
            0,
            4,
            0,
            4,
        )

        stations_grid.setHorizontalSpacing(
            18
        )

        stations_grid.setVerticalSpacing(
            18
        )

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

            card.cast_requested.connect(
                self.start_casting
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

        scroll_area.setWidgetResizable(
            True
        )

        scroll_area.setFrameShape(
            QScrollArea.Shape.NoFrame
        )

        scroll_area.setWidget(
            content_widget
        )

        footer_layout = QHBoxLayout()

        footer_brand = QLabel(
            "VR GAMES BÁVARO"
        )

        footer_brand.setStyleSheet(
            """
            color: #00A8FF;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        footer_version = QLabel(
            "VERSIÓN 1.0.0"
        )

        footer_version.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        footer_version.setStyleSheet(
            """
            color: #8290A8;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        footer_author = QLabel(
            "POWERED BY NELPHY PEÑA"
        )

        footer_author.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        footer_author.setStyleSheet(
            """
            color: #FF2BC2;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            """
        )

        footer_layout.addWidget(
            footer_brand
        )

        footer_layout.addStretch()

        footer_layout.addWidget(
            footer_version
        )

        footer_layout.addStretch()

        footer_layout.addWidget(
            footer_author
        )

        main_layout.addWidget(
            self.top_bar
        )

        main_layout.addLayout(
            actions_layout
        )

        main_layout.addWidget(
            scroll_area
        )

        main_layout.addLayout(
            footer_layout
        )

        self.quest_controller = (
            QuestController()
        )

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
        wizard = QuestSetupWizard(
            self
        )

        wizard.exec()

        self.quest_controller.reload_stations()

    def open_tv_setup(self):
        dialog = TvSetupDialog(
            self
        )

        dialog.exec()

    def update_quest_devices(
        self,
        devices: list,
    ):
        self.top_bar.update_metrics(
            devices
        )

        for card in self.station_cards:
            card.update_device_status(
                False
            )

        for device in devices:
            station_index = (
                device["station_number"] - 1
            )

            if not (
                0
                <= station_index
                < len(self.station_cards)
            ):
                continue

            self.station_cards[
                station_index
            ].update_device_status(
                connected=(
                    device["connected"]
                ),
                battery=device["battery"],
                serial=(
                    device["adb_identifier"]
                ),
                games=device.get(
                    "games",
                    [],
                ),
            )

    def start_casting(
        self,
        card: StationCard,
        station_number: int,
        station_name: str,
        adb_identifier: str,
    ):
        if not adb_identifier:
            card.cast_failed()

            QMessageBox.warning(
                self,
                "Meta desconectada",
                (
                    f"{station_name} no está "
                    "conectada por ADB."
                ),
            )
            return

        display_manager = DisplayManager()

        display = (
            display_manager.get_display_for_station(
                station_number
            )
        )

        if not display:
            card.cast_failed()

            QMessageBox.warning(
                self,
                "TV no asignada",
                (
                    "No hay una televisión asignada "
                    f"a {station_name}.\n\n"
                    "Utiliza CONFIGURAR TVs."
                ),
            )
            return

        receiver_name = (
            display.get(
                "device_name",
                "",
            ).strip()
        )

        television_ip = (
            display.get(
                "ip",
                "",
            ).strip()
        )

        if not receiver_name:
            card.cast_failed()

            QMessageBox.warning(
                self,
                "TV sin configurar",
                (
                    "La estación no tiene un nombre "
                    "Chromecast configurado.\n\n"
                    "Utiliza CONFIGURAR TVs."
                ),
            )
            return

        if station_number in self.cast_threads:
            QMessageBox.information(
                self,
                "Transmisión en proceso",
                (
                    f"{station_name} ya está "
                    "intentando conectarse."
                ),
            )
            return

        card.cast_connecting()

        thread = QThread(
            self
        )

        worker = CastWorker(
            card=card,
            adb_identifier=adb_identifier,
            receiver_name=receiver_name,
            television_ip=television_ip,
        )

        worker.moveToThread(
            thread
        )

        thread.started.connect(
            worker.run
        )

        worker.finished.connect(
            self.cast_finished
        )

        worker.finished.connect(
            thread.quit
        )

        worker.finished.connect(
            worker.deleteLater
        )

        thread.finished.connect(
            thread.deleteLater
        )

        thread.finished.connect(
            lambda number=station_number:
            self.cast_threads.pop(
                number,
                None,
            )
        )

        self.cast_threads[
            station_number
        ] = {
            "thread": thread,
            "worker": worker,
        }

        thread.start()

    @Slot(bool, str, object)
    def cast_finished(
        self,
        success: bool,
        message: str,
        card: StationCard,
    ):
        if success:
            card.cast_started()

            QMessageBox.information(
                self,
                "Transmisión iniciada",
                message,
            )
            return

        card.cast_failed()

        QMessageBox.warning(
            self,
            "No se pudo transmitir",
            message,
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