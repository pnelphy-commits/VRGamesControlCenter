from services.adb_service import AdbService
from services.game_manager import GameManager
from services.station_manager import StationManager


class DiscoveryService:
    def __init__(self):
        self.adb = AdbService()
        self.game_manager = GameManager(self.adb)
        self.station_manager = StationManager()

    def discover_stations(self) -> list[dict]:
        """
        Busca una vez las estaciones registradas.

        No mantiene ciclos permanentes ni hace varios intentos
        continuos de reconexión.
        """

        self.reload_stations()
        self._connect_saved_stations_once()

        discovered = []

        for adb_identifier in self.adb.get_connected_devices():
            serial = self.adb.get_device_serial(adb_identifier)

            if not serial:
                continue

            station = self.station_manager.get_station_by_serial(
                serial
            )

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

    def _connect_saved_stations_once(self):
        """
        Hace un solo intento de conexión por estación.
        Evita ciclos largos cuando una Quest no responde.
        """

        connected_devices = set(
            self.adb.get_connected_devices()
        )

        for station in self.station_manager.stations:
            ip_address = station.get("ip", "").strip()

            if not ip_address:
                continue

            wifi_identifier = f"{ip_address}:5555"

            if wifi_identifier in connected_devices:
                continue

            self.adb.connect_device(
                wifi_identifier,
                timeout=2,
            )

    def reconnect_station(
        self,
        station_number: int,
    ) -> bool:
        """
        Reconecta una estación específica cuando el operador
        solicita preparar o actualizar las estaciones.
        """

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
                f"La META QUEST {station_number} "
                "no tiene una IP guardada."
            )
            return False

        wifi_identifier = f"{ip_address}:5555"

        if self.adb.is_device_connected(wifi_identifier):
            return True

        return self.adb.connect_device(
            wifi_identifier,
            timeout=3,
        )

    def reload_stations(self):
        self.station_manager.stations = (
            self.station_manager.load_stations()
        )