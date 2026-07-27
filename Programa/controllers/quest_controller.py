from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from services.discovery_service import DiscoveryService


class DiscoveryWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        discovery_service: DiscoveryService,
    ):
        super().__init__()

        self.discovery_service = discovery_service

    @Slot()
    def run(self):
        try:
            devices = (
                self.discovery_service.discover_stations()
            )
            self.finished.emit(devices)

        except Exception as error:
            self.failed.emit(str(error))


class QuestController(QObject):
    devices_updated = Signal(object)

    def __init__(self):
        super().__init__()

        self.discovery_service = DiscoveryService()

        self.discovery_thread = None
        self.discovery_worker = None
        self.discovery_in_progress = False
        self.shutting_down = False

        # Solo se ejecuta una búsqueda al abrir el programa.
        # No habrá un temporizador buscando continuamente.
        QTimer.singleShot(500, self.refresh_devices)

    def refresh_devices(self):
        if self.shutting_down:
            return

        if self.discovery_in_progress:
            return

        self.discovery_in_progress = True

        self.discovery_thread = QThread(self)

        self.discovery_worker = DiscoveryWorker(
            self.discovery_service
        )

        self.discovery_worker.moveToThread(
            self.discovery_thread
        )

        self.discovery_thread.started.connect(
            self.discovery_worker.run
        )

        self.discovery_worker.finished.connect(
            self.handle_discovery_finished
        )

        self.discovery_worker.failed.connect(
            self.handle_discovery_failed
        )

        self.discovery_worker.finished.connect(
            self.discovery_thread.quit
        )

        self.discovery_worker.failed.connect(
            self.discovery_thread.quit
        )

        self.discovery_thread.finished.connect(
            self.cleanup_discovery
        )

        self.discovery_thread.start()

    def handle_discovery_finished(
        self,
        devices,
    ):
        if not self.shutting_down:
            self.devices_updated.emit(devices)

    def handle_discovery_failed(
        self,
        error_message: str,
    ):
        print(
            "Error al buscar Meta Quest: "
            f"{error_message}"
        )

        if not self.shutting_down:
            self.devices_updated.emit([])

    def cleanup_discovery(self):
        if self.discovery_worker is not None:
            self.discovery_worker.deleteLater()

        if self.discovery_thread is not None:
            self.discovery_thread.deleteLater()

        self.discovery_worker = None
        self.discovery_thread = None
        self.discovery_in_progress = False

    def reload_stations(self):
        self.discovery_service.reload_stations()
        self.refresh_devices()

    def launch_game(
        self,
        adb_identifier: str,
        component: str,
    ) -> bool:
        if not adb_identifier:
            self.discovery_service.adb.last_error = (
                "La Meta Quest no tiene conexión ADB."
            )
            return False

        if not component:
            self.discovery_service.adb.last_error = (
                "No se seleccionó un juego válido."
            )
            return False

        return self.discovery_service.adb.launch_activity(
            adb_identifier,
            component,
        )

    def finish_session(
        self,
        adb_identifier: str,
    ) -> bool:
        if not adb_identifier:
            self.discovery_service.adb.last_error = (
                "La Meta Quest no tiene conexión ADB."
            )
            return False

        return self.discovery_service.adb.close_activity(
            adb_identifier
        )

    def get_last_error(self) -> str:
        return self.discovery_service.adb.last_error

    def shutdown(self):
        """
        Cierra correctamente el hilo de búsqueda antes
        de terminar la aplicación.
        """

        self.shutting_down = True

        if (
            self.discovery_thread is not None
            and self.discovery_thread.isRunning()
        ):
            self.discovery_thread.quit()

            if not self.discovery_thread.wait(5000):
                print(
                    "La búsqueda ADB tardó demasiado "
                    "en finalizar."
                )