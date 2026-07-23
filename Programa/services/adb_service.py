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

    def run_command(
        self,
        *args: str,
        timeout: int = 5,
    ) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [str(self.adb_path), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

        except subprocess.TimeoutExpired:
            self.last_error = (
                f"El comando ADB tardó más de {timeout} segundos."
            )

            return subprocess.CompletedProcess(
                args=[str(self.adb_path), *args],
                returncode=1,
                stdout="",
                stderr=self.last_error,
            )

        except OSError as error:
            self.last_error = str(error)

            return subprocess.CompletedProcess(
                args=[str(self.adb_path), *args],
                returncode=1,
                stdout="",
                stderr=self.last_error,
            )

    def get_connected_devices(self) -> list[str]:
        result = self.run_command(
            "devices",
            timeout=3,
        )

        devices = []

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) == 2 and parts[1] == "device":
                devices.append(parts[0])

        return devices

    def get_all_device_states(self) -> dict[str, str]:
        result = self.run_command(
            "devices",
            timeout=3,
        )

        states = {}

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) == 2:
                identifier, status = parts
                states[identifier] = status

        return states

    def connect_device(
        self,
        adb_identifier: str,
        timeout: int = 4,
    ) -> bool:
        self.last_error = ""

        result = self.run_command(
            "connect",
            adb_identifier,
            timeout=timeout,
        )

        output = (
            f"{result.stdout}\n{result.stderr}"
        ).strip()

        if (
            "connected to" in output
            or "already connected to" in output
        ):
            return True

        self.last_error = output or (
            f"No se pudo conectar con {adb_identifier}."
        )

        return False

    def disconnect_device(
        self,
        adb_identifier: str,
    ) -> bool:
        result = self.run_command(
            "disconnect",
            adb_identifier,
            timeout=3,
        )

        return result.returncode == 0

    def is_device_connected(
        self,
        adb_identifier: str,
    ) -> bool:
        states = self.get_all_device_states()

        return states.get(adb_identifier) == "device"

    def get_device_serial(
        self,
        adb_identifier: str,
    ) -> str:
        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "getprop",
            "ro.serialno",
            timeout=4,
        )

        return result.stdout.strip()

    def get_battery_level(
        self,
        adb_identifier: str,
    ) -> int | None:
        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "dumpsys",
            "battery",
            timeout=4,
        )

        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("level:"):
                try:
                    return int(
                        line.split(":", 1)[1].strip()
                    )
                except ValueError:
                    return None

        return None

    def wake_device(
        self,
        adb_identifier: str,
    ) -> bool:
        self.last_error = ""

        if not self.is_device_connected(adb_identifier):
            self.last_error = (
                "La Meta Quest no está conectada por ADB."
            )
            return False

        result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "input",
            "keyevent",
            "224",
            timeout=4,
        )

        if result.returncode != 0:
            self.last_error = (
                result.stderr.strip()
                or "No se pudo despertar la Meta Quest."
            )
            return False

        return True

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
            timeout=8,
        )

        output = (
            f"{result.stdout}\n{result.stderr}"
        ).strip()

        if result.returncode != 0:
            self.last_error = output or (
                "ADB devolvió un error."
            )
            return False

        if (
            "Error type" in output
            or "does not exist" in output
            or "not found" in output
        ):
            self.last_error = output
            return False

        if (
            "Starting:" not in output
            and "Warning:" not in output
        ):
            self.last_error = output or (
                "No se recibió confirmación de inicio."
            )
            return False

        return True

    def close_activity(
        self,
        adb_identifier: str,
        component: str = "",
    ) -> bool:
        """
        Cierra todas las aplicaciones instaladas por el usuario
        en una Meta Quest específica y regresa al menú principal.

        No detiene procesos internos de Horizon OS.
        """

        self.last_error = ""

        if not self.is_device_connected(adb_identifier):
            self.last_error = (
                "La Meta Quest no está conectada por ADB."
            )
            return False

        packages_result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "pm",
            "list",
            "packages",
            "-3",
            timeout=8,
        )

        if packages_result.returncode != 0:
            self.last_error = (
                packages_result.stderr.strip()
                or "No se pudo obtener la lista de aplicaciones."
            )
            return False

        packages = []

        for line in packages_result.stdout.splitlines():
            line = line.strip()

            if not line.startswith("package:"):
                continue

            package_name = line.replace(
                "package:",
                "",
                1,
            ).strip()

            if package_name:
                packages.append(package_name)

        if not packages:
            self.last_error = (
                "No se encontraron aplicaciones instaladas "
                "por el usuario."
            )
            return False

        failed_packages = []

        for package_name in packages:
            result = self.run_command(
                "-s",
                adb_identifier,
                "shell",
                "am",
                "force-stop",
                package_name,
                timeout=4,
            )

            if result.returncode != 0:
                failed_packages.append(package_name)

        home_result = self.run_command(
            "-s",
            adb_identifier,
            "shell",
            "input",
            "keyevent",
            "3",
            timeout=4,
        )

        if home_result.returncode != 0:
            self.last_error = (
                home_result.stderr.strip()
                or (
                    "Las aplicaciones se cerraron, pero no fue "
                    "posible regresar al menú principal."
                )
            )
            return False

        if failed_packages:
            self.last_error = (
                "Algunas aplicaciones no pudieron cerrarse: "
                + ", ".join(failed_packages)
            )
            return False

        return True