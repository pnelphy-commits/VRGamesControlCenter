import platform
import subprocess


class NetworkService:
    @staticmethod
    def ping_device(
        ip_address: str,
        timeout_seconds: int = 2,
    ) -> tuple[bool, str]:
        ip_address = ip_address.strip()

        if not ip_address:
            return False, "La dirección IP está vacía."

        system_name = platform.system().lower()

        if system_name == "windows":
            command = [
                "ping",
                "-n",
                "1",
                "-w",
                str(timeout_seconds * 1000),
                ip_address,
            ]
        else:
            command = [
                "ping",
                "-c",
                "1",
                "-W",
                str(timeout_seconds),
                ip_address,
            ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds + 2,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if system_name == "windows"
                    else 0
                ),
            )

        except subprocess.TimeoutExpired:
            return False, "La prueba agotó el tiempo de espera."

        except OSError as error:
            return False, f"No se pudo ejecutar ping: {error}"

        if result.returncode == 0:
            return True, f"El dispositivo {ip_address} está en línea."

        return False, f"El dispositivo {ip_address} no respondió."