import json
import ipaddress
from pathlib import Path


class DisplayManager:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        self.config_path = (
            project_root
            / "Config"
            / "displays.json"
        )

        self.displays = self.load_displays()

    def load_displays(self) -> list[dict]:
        if not self.config_path.exists():
            displays = self.create_default_displays()
            self.displays = displays
            self.save_displays()
            return displays

        try:
            with self.config_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            displays = data.get("displays", [])

            if not isinstance(displays, list):
                return self.create_default_displays()

            return displays

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return self.create_default_displays()

    @staticmethod
    def create_default_displays() -> list[dict]:
        return [
            {
                "display_number": number,
                "name": f"TV META {number}",
                "device_name": "",
                "ip": "",
                "assigned_station": number,
            }
            for number in range(1, 5)
        ]

    def reload(self):
        self.displays = self.load_displays()

    def save_displays(self) -> bool:
        try:
            self.config_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            data = {
                "displays": self.displays,
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

            return True

        except OSError:
            return False

    def get_display_by_number(
        self,
        display_number: int,
    ) -> dict | None:
        for display in self.displays:
            if (
                display.get("display_number")
                == display_number
            ):
                return display

        return None

    def get_display_for_station(
        self,
        station_number: int,
    ) -> dict | None:
        for display in self.displays:
            if (
                display.get("assigned_station")
                == station_number
            ):
                return display

        return None

    def update_display(
        self,
        display_number: int,
        device_name: str,
        ip_address: str,
    ) -> tuple[bool, str]:
        display = self.get_display_by_number(
            display_number
        )

        if not display:
            return (
                False,
                "No se encontró el televisor.",
            )

        device_name = device_name.strip()
        ip_address = ip_address.strip()

        if ip_address:
            try:
                ipaddress.ip_address(ip_address)

            except ValueError:
                return (
                    False,
                    "La dirección IP no es válida.",
                )

        display["device_name"] = device_name
        display["ip"] = ip_address

        if not self.save_displays():
            return (
                False,
                "No fue posible guardar la configuración.",
            )

        return (
            True,
            "Configuración del televisor guardada.",
        )

    def assign_display_to_station(
        self,
        display_number: int,
        station_number: int,
    ) -> tuple[bool, str]:
        selected_display = self.get_display_by_number(
            display_number
        )

        if not selected_display:
            return (
                False,
                "No se encontró el televisor.",
            )

        # Quitamos esta estación de cualquier otra TV.
        for display in self.displays:
            if (
                display.get("assigned_station")
                == station_number
            ):
                display["assigned_station"] = None

        selected_display["assigned_station"] = (
            station_number
        )

        if not self.save_displays():
            return (
                False,
                "No fue posible guardar la asignación.",
            )

        return (
            True,
            (
                f"TV META {display_number} asignada "
                f"a META QUEST {station_number}."
            ),
        )

    @staticmethod
    def is_display_configured(
        display: dict | None,
    ) -> bool:
        if not display:
            return False

        return bool(
            display.get("device_name")
            and display.get("ip")
        )