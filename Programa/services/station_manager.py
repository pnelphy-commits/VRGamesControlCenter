import json
from pathlib import Path


class StationManager:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        self.config_path = project_root / "Config" / "stations.json"

        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.stations = self.load_stations()

    def load_stations(self) -> list[dict]:
        if not self.config_path.exists():
            return []

        try:
            with self.config_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return data.get("stations", [])
        except (OSError, json.JSONDecodeError):
            return []

    def save_stations(self):
        data = {
            "stations": self.stations,
        }

        with self.config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def assign_station(
        self,
        station_number: int,
        serial: str,
        ip: str = "",
    ):
        station_name = f"META QUEST {station_number}"

        existing_station = self.get_station_by_serial(serial)

        if existing_station:
            existing_station["station_number"] = station_number
            existing_station["name"] = station_name
            existing_station["ip"] = ip
        else:
            self.stations.append(
                {
                    "station_number": station_number,
                    "name": station_name,
                    "serial": serial,
                    "ip": ip,
                }
            )

        self.stations.sort(
            key=lambda station: station["station_number"]
        )

        self.save_stations()

    def get_station_by_serial(
        self,
        serial: str,
    ) -> dict | None:
        for station in self.stations:
            if station.get("serial") == serial:
                return station

        return None

    def get_station_by_number(
        self,
        station_number: int,
    ) -> dict | None:
        for station in self.stations:
            if station.get("station_number") == station_number:
                return station

        return None