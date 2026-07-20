import re

from services.adb_service import AdbService


class QuestSetupService:
    def __init__(self):
        self.adb = AdbService()
        self.last_error = ""

    def get_usb_devices(self) -> list[str]:
        result = self.adb.run_command("devices")
        usb_devices = []

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) != 2:
                continue

            identifier, status = parts

            if status == "device" and ":" not in identifier:
                usb_devices.append(identifier)

        return usb_devices

    def configure_usb_device(self, usb_serial: str) -> dict | None:
        self.last_error = ""

        if not usb_serial:
            self.last_error = "No se encontró ninguna Meta Quest por USB."
            return None

        serial = self._get_physical_serial(usb_serial)

        if not serial:
            self.last_error = "No se pudo obtener el serial del visor."
            return None

        ip_address = self._get_wifi_ip(usb_serial)

        if not ip_address:
            self.last_error = (
                "No se pudo obtener la dirección IP. "
                "Verifica que la Meta Quest esté conectada al Wi-Fi."
            )
            return None

        tcp_result = self.adb.run_command(
            "-s",
            usb_serial,
            "tcpip",
            "5555",
        )

        tcp_output = (
            f"{tcp_result.stdout}\n{tcp_result.stderr}"
        ).strip()

        if (
            tcp_result.returncode != 0
            or "restarting in TCP mode" not in tcp_output
        ):
            self.last_error = tcp_output or (
                "No se pudo activar ADB por Wi-Fi."
            )
            return None

        wifi_identifier = f"{ip_address}:5555"

        connect_result = self.adb.run_command(
            "connect",
            wifi_identifier,
        )

        connect_output = (
            f"{connect_result.stdout}\n{connect_result.stderr}"
        ).strip()

        if (
            "connected to" not in connect_output
            and "already connected to" not in connect_output
        ):
            self.last_error = connect_output or (
                "No se pudo conectar la Meta Quest por Wi-Fi."
            )
            return None

        if not self._verify_wifi_connection(wifi_identifier):
            self.last_error = (
                "La conexión Wi-Fi se inició, pero ADB no confirmó el visor."
            )
            return None

        return {
            "serial": serial,
            "ip": ip_address,
            "adb_identifier": wifi_identifier,
        }

    def _get_physical_serial(self, adb_identifier: str) -> str:
        result = self.adb.run_command(
            "-s",
            adb_identifier,
            "shell",
            "getprop",
            "ro.serialno",
        )

        return result.stdout.strip()

    def _get_wifi_ip(self, adb_identifier: str) -> str:
        result = self.adb.run_command(
            "-s",
            adb_identifier,
            "shell",
            "ip",
            "route",
        )

        match = re.search(
            r"\bsrc\s+(\d{1,3}(?:\.\d{1,3}){3})",
            result.stdout,
        )

        if not match:
            return ""

        return match.group(1)

    def _verify_wifi_connection(
        self,
        wifi_identifier: str,
    ) -> bool:
        result = self.adb.run_command("devices")

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) != 2:
                continue

            identifier, status = parts

            if (
                identifier == wifi_identifier
                and status == "device"
            ):
                return True

        return False