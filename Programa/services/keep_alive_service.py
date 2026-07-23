from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from services.adb_service import AdbService
from services.station_manager import StationManager


class KeepAliveWorker(QObject):
    finished = Signal(object)

    def __init__(
        self,
        adb: AdbService,
        stations: list[dict],
    ):
        super().__init__()

        self.adb = adb
        self.stations = stations

    @Slot()
    def run(self):
        results = {}

        for station in self.stations:
            station_number = station.get("station_number")
            ip_address = station.get("ip", "").strip()
            expected_serial = station.get("serial", "").strip()

            if not station_number or not ip_address:
                continue

            adb_identifier = f"{ip_address}:5555"

            station_result = {
                "station_number": station_number,
                "adb_identifier": adb_identifier,
                "connected": False,
                "serial": "",
                "error": "",
            }

            if not self.adb.is_device_connected(adb_identifier):
                self.adb.connect_device(
                    adb_identifier,
                    timeout=3,
                )

            if not self.adb.is_device_connected(adb_identifier):
                station_result["error"] = (
                    self.adb.last_error
                    or "La Meta Quest no responde por ADB."
                )
                results[station_number] = station_result
                continue

            serial = self.adb.get_device_serial(adb_identifier)

            if not serial:
                station_result["error"] = (
                    self.adb.last_error
                    or "No se pudo leer el serial."
                )
                results[station_number] = station_result
                continue

            if expected_serial and serial != expected_serial:
                station_result["error"] = (
                    "La IP corresponde a otra Meta Quest."
                )
                station_result["serial"] = serial
                results[station_number] = station_result
                continue

            station_result["connected"] = True
            station_result["serial"] = serial
            results[station_number] = station_result

        self.finished.emit(results)


class KeepAliveService(QObject):
    status_updated = Signal(object)

    def __init__(
        self,
        interval_seconds: int = 20,
        parent=None,
    ):
        super().__init__(parent)

        self.adb = AdbService()
        self.station_manager = StationManager()

        self.interval_seconds = interval_seconds
        self.worker_running = False

        self.thread = None
        self.worker = None

        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_seconds * 1000)
        self.timer.timeout.connect(self.run_check)

    def start(self):
        if not self.timer.isActive():
            self.timer.start()

        QTimer.singleShot(1000, self.run_check)

    def stop(self):
        self.timer.stop()

    def run_check(self):
        if self.worker_running:
            return

        self.station_manager.stations = (
            self.station_manager.load_stations()
        )

        stations = list(self.station_manager.stations)

        if not stations:
            self.status_updated.emit({})
            return

        self.worker_running = True

        self.thread = QThread(self)
        self.worker = KeepAliveWorker(
            self.adb,
            stations,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_results)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_worker)

        self.thread.start()

    def handle_results(self, results):
        self.status_updated.emit(results)

    def cleanup_worker(self):
        if self.worker is not None:
            self.worker.deleteLater()

        if self.thread is not None:
            self.thread.deleteLater()

        self.worker = None
        self.thread = None
        self.worker_running = False