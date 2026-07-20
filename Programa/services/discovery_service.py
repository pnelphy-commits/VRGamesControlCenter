from services.adb_service import AdbService
from services.game_manager import GameManager
from services.station_manager import StationManager


class DiscoveryService:
    def __init__(self):
        self.adb = AdbService()
        self.game_manager = GameManager(self.adb)
        self.station_manager = StationManager()

    def discover_stations(self) -> list[dict]:
        self._reconnect_saved_stations()

        discovered = []

        for adb_identifier in self.adb.get_connected_devices():
            serial = self.adb.get_device_serial(adb_identifier)
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

            self.adb.run_command(
                "connect",
                wifi_identifier,
            )

    def reload_stations(self):
        self.station_manager.stations = (
            self.station_manager.load_stations()
        )