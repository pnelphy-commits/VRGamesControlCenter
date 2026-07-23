import time

from services.adb_service import AdbService
from services.game_manager import GameManager
from services.station_manager import StationManager


class DiscoveryService:
    def __init__(self):
        self.adb = AdbService()
        self.game_manager = GameManager(self.adb)
        self.station_manager = StationManager()

    def discover_stations(self) -> list[dict]:
        self.reload_stations()
        self._reconnect_saved_stations()

        discovered = []

        connected_devices = self.adb.get_connected_devices()

        for adb_identifier in connected_devices:
            serial = self.adb.get_device_serial(adb_identifier)

            if not serial:
                continue

            station = self.station_manager.get_station_by_serial(serial)

            if not station:
                continue

            games = self.game_manager.get_installed_games(
                adb_identifier
            )

            discovered.append(
                {
                    "station_number": station["station_number"],
                    "name": station["name"],
                    "serial": serial,
                    "ip": station.get("ip", ""),
                    "adb_identifier": adb_identifier,
                    "connected": True,
                    "battery": self.adb.get_battery_level(
                        adb_identifier
                    ),
                    "games": [
                        {
                            "name": game.name,
                            "component": game.component,
                        }
                        for game in games
                    ],
                }
            )

        discovered.sort(
            key=lambda device: device["station_number"]
        )

        return discovered

    def _reconnect_saved_stations(self):
        for station in self.station_manager.stations:
            ip_address = station.get("ip", "").strip()

            if not ip_address:
                continue

            wifi_identifier = f"{ip_address}:5555"

            if self.adb.is_device_connected(wifi_identifier):
                continue

            self._connect_with_retries(
                wifi_identifier,
                attempts=3,
            )

    def _connect_with_retries(
        self,
        adb_identifier: str,
        attempts: int = 3,
    ) -> bool:
        for attempt in range(attempts):
            self.adb.disconnect_device(adb_identifier)

            if self.adb.connect_device(
                adb_identifier,
                timeout=4,
            ):
                time.sleep(0.5)

                if self.adb.is_device_connected(adb_identifier):
                    return True

            if attempt < attempts - 1:
                time.sleep(1)

        return False

    def reconnect_station(
        self,
        station_number: int,
    ) -> bool:
        self.reload_stations()

        station = self.station_manager.get_station_by_number(
            station_number
        )

        if not station:
            self.adb.last_error = (
                f"No existe la META QUEST {station_number} "
                "en la configuración."
            )
            return False

        ip_address = station.get("ip", "").strip()

        if not ip_address:
            self.adb.last_error = (
                f"La META QUEST {station_number} no tiene una IP guardada."
            )
            return False

        wifi_identifier = f"{ip_address}:5555"

        if self.adb.is_device_connected(wifi_identifier):
            return True

        return self._connect_with_retries(
            wifi_identifier,
            attempts=3,
        )

    def wake_station(
        self,
        station_number: int,
    ) -> bool:
        station = self.station_manager.get_station_by_number(
            station_number
        )

        if not station:
            self.adb.last_error = (
                f"No existe la META QUEST {station_number}."
            )
            return False

        ip_address = station.get("ip", "").strip()

        if not ip_address:
            self.adb.last_error = (
                f"La META QUEST {station_number} no tiene una IP guardada."
            )
            return False

        wifi_identifier = f"{ip_address}:5555"

        if not self.adb.is_device_connected(wifi_identifier):
            if not self.reconnect_station(station_number):
                return False

        return self.adb.wake_device(wifi_identifier)

    def reload_stations(self):
        self.station_manager.stations = (
            self.station_manager.load_stations()
        )