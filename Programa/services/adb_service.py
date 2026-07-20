import subprocess
from pathlib import Path


class AdbService:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        self.adb_path = (
            project_root
            / "tools"
            / "platform-tools"
            / "adb.exe"
        )

        self.last_error = ""

    def run_command(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(self.adb_path), *args],
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def get_connected_devices(self) -> list[str]:
        result = self.run_command("devices")
        devices = []

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) == 2 and parts[1] == "device":
                devices.append(parts[0])

        return devices

    def get_device_serial(self, adb_identifier: str) -> str:
        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "getprop",
            "ro.serialno",
        )

        serial = result.stdout.strip()

        if serial:
            return serial

        return adb_identifier.split(":", 1)[0]

    def get_battery_level(self, adb_identifier: str) -> int | None:
        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "dumpsys",
            "battery",
        )

        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("level:"):
                try:
                    return int(line.split(":", 1)[1].strip())
                except ValueError:
                    return None

        return None

    def launch_activity(
        self,
        adb_identifier: str,
        component: str,
    ) -> bool:
        self.last_error = ""

        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "am",
            "start",
            "-n",
            component,
        )

        output = f"{result.stdout}\n{result.stderr}".strip()

        if result.returncode != 0:
            self.last_error = output or "ADB devolvió un error."
            return False

        if "Error type" in output or "does not exist" in output:
            self.last_error = output
            return False

        if "Starting:" not in output and "Warning:" not in output:
            self.last_error = output or "No se recibió confirmación de inicio."
            return False

        return True