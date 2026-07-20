from PySide6.QtCore import QObject, QTimer, Signal

from services.adb_service import AdbService
from services.game_manager import GameManager


class QuestController(QObject):
    devices_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.adb = AdbService()
        self.game_manager = GameManager(self.adb)

        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start()

        QTimer.singleShot(200, self.refresh_devices)

    def refresh_devices(self):
        devices = []

        for serial in self.adb.get_connected_devices():
            games = self.game_manager.get_installed_games(serial)

            devices.append(
                {
                    "serial": serial,
                    "battery": self.adb.get_battery_level(serial),
                    "connected": True,
                    "games": [
                        {
                            "name": game.name,
                            "component": game.component,
                        }
                        for game in games
                    ],
                }
            )

        self.devices_updated.emit(devices)

    def launch_game(self, serial: str, component: str) -> bool:
        if not serial:
            self.adb.last_error = "La Meta Quest no tiene un serial asignado."
            return False

        if not component:
            self.adb.last_error = "No se seleccionó un juego válido."
            return False

        return self.adb.launch_activity(serial, component)

    def get_last_error(self) -> str:
        return self.adb.last_error