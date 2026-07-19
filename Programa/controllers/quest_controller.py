from PySide6.QtCore import QObject, QTimer, Signal

from services.adb_service import AdbService


class QuestController(QObject):
    devices_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.adb = AdbService()

        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start()

        self.refresh_devices()

    def refresh_devices(self):
        devices = []

        for serial in self.adb.get_connected_devices():
            battery = self.adb.get_battery_level(serial)

            devices.append(
                {
                    "serial": serial,
                    "battery": battery,
                    "connected": True,
                }
            )

        self.devices_updated.emit(devices)