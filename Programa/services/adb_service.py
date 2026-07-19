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

    def run_command(self, *args: str) -> str:
        result = subprocess.run(
            [str(self.adb_path), *args],
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    def get_connected_devices(self) -> list[str]:
        output = self.run_command("devices")
        devices = []

        for line in output.splitlines()[1:]:
            parts = line.split()

            if len(parts) == 2 and parts[1] == "device":
                devices.append(parts[0])

        return devices

    def get_battery_level(self, serial: str) -> int | None:
        output = self.run_command(
            "-s",
            serial,
            "shell",
            "dumpsys",
            "battery",
        )

        for line in output.splitlines():
            line = line.strip()

            if line.startswith("level:"):
                return int(line.split(":", 1)[1].strip())

        return None
    