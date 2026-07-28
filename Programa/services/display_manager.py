import ipaddress
import json
from pathlib import Path


class DisplayManager:
    TOTAL_DISPLAYS = 4

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        self.config_path = (
            project_root
            / "Config"
            / "displays.json"
        )

        self.displays = self.load_displays()

    @classmethod
    def create_default_displays(cls) -> list[dict]:
        return [
            {
                "display_number": number,
                "name": f"TV META {number}",
                "device_name": "",
                "ip": "",
                "assigned_station": number,
            }
            for number in range(
                1,
                cls.TOTAL_DISPLAYS + 1,
            )
        ]

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

        except (
            OSError,
            json.JSONDecodeError,
        ):
            displays = self.create_default_displays()

            self.displays = displays
            self.save_displays()

            return displays

        displays = data.get(
            "displays",
            [],
        )

        if not isinstance(displays, list):
            displays = []

        normalized_displays = []

        for number in range(
            1,
            self.TOTAL_DISPLAYS + 1,
        ):
            existing_display = next(
                (
                    display
                    for display in displays
                    if display.get(
                        "display_number"
                    )
                    == number
                ),
                None,
            )

            if existing_display:
                normalized_displays.append(
                    {
                        "display_number": number,
                        "name": existing_display.get(
                            "name",
                            f"TV META {number}",
                        ),
                        "device_name": existing_display.get(
                            "device_name",
                            "",
                        ),
                        "ip": existing_display.get(
                            "ip",
                            "",
                        ),
                        "assigned_station": (
                            existing_display.get(
                                "assigned_station",
                                number,
                            )
                        ),
                    }
                )

            else:
                normalized_displays.append(
                    {
                        "display_number": number,
                        "name": f"TV META {number}",
                        "device_name": "",
                        "ip": "",
                        "assigned_station": number,
                    }
                )

        return normalized_displays

    def reload(self):
        self.displays = self.load_displays()

    def save_displays(self) -> bool:
        try:
            self.config_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.config_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    {
                        "displays": self.displays,
                    },
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

    @staticmethod
    def validate_ip(
        ip_address: str,
    ) -> tuple[bool, str]:
        ip_address = ip_address.strip()

        if not ip_address:
            return (
                False,
                "Debes escribir la dirección IP de la TV.",
            )

        try:
            ipaddress.ip_address(
                ip_address
            )

        except ValueError:
            return (
                False,
                "La dirección IP escrita no es válida.",
            )

        return True, ""

    def save_display_configuration(
        self,
        display_number: int,
        device_name: str,
        ip_address: str,
        assigned_station: int,
    ) -> tuple[bool, str]:
        display = self.get_display_by_number(
            display_number
        )

        if not display:
            return (
                False,
                "No se encontró la TV seleccionada.",
            )

        device_name = device_name.strip()
        ip_address = ip_address.strip()

        if not device_name:
            return (
                False,
                (
                    "Debes escribir el nombre exacto "
                    "del Chromecast."
                ),
            )

        valid_ip, ip_message = self.validate_ip(
            ip_address
        )

        if not valid_ip:
            return False, ip_message

        if assigned_station not in (
            1,
            2,
            3,
            4,
        ):
            return (
                False,
                "La estación seleccionada no es válida.",
            )

        # Una estación solo puede tener una TV.
        for other_display in self.displays:
            if (
                other_display.get(
                    "display_number"
                )
                != display_number
                and other_display.get(
                    "assigned_station"
                )
                == assigned_station
            ):
                other_display[
                    "assigned_station"
                ] = None

        display["name"] = (
            f"TV META {display_number}"
        )

        display["device_name"] = (
            device_name
        )

        display["ip"] = ip_address

        display["assigned_station"] = (
            assigned_station
        )

        if not self.save_displays():
            return (
                False,
                (
                    "No se pudo guardar la "
                    "configuración de la TV."
                ),
            )

        return (
            True,
            (
                f"{device_name} fue asignada "
                f"a META QUEST {assigned_station}."
            ),
        )

    def clear_display(
        self,
        display_number: int,
    ) -> tuple[bool, str]:
        display = self.get_display_by_number(
            display_number
        )

        if not display:
            return (
                False,
                "No se encontró la TV seleccionada.",
            )

        display["device_name"] = ""
        display["ip"] = ""
        display["assigned_station"] = None

        if not self.save_displays():
            return (
                False,
                "No se pudo eliminar la configuración.",
            )

        return (
            True,
            (
                f"TV META {display_number} "
                "quedó sin configurar."
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
            and display.get(
                "assigned_station"
            )
        )