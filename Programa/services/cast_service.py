import re
import subprocess
import time
from pathlib import Path
from xml.dom import minidom


class CastService:
    REMOTE_XML_PATH = "/sdcard/vrgames_cast_ui.xml"

    CAST_PACKAGE = "com.oculus.metacam"

    CAST_ACTIVITY = (
        "com.oculus.metacam/"
        ".dialogactivity.SharingDialogActivity"
    )

    CAST_ACTION = "START_CASTING"

    RECEIVER_FALLBACK_COORDINATES = (240, 383)
    NEXT_FALLBACK_COORDINATES = (240, 637)

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        self.adb_path = (
            project_root
            / "tools"
            / "platform-tools"
            / "adb.exe"
        )

        self.last_error = ""

    def run_adb(
        self,
        device_identifier: str,
        arguments: list[str],
        timeout: int = 30,
    ) -> subprocess.CompletedProcess:
        command = [
            str(self.adb_path),
            "-s",
            device_identifier,
            *arguments,
        ]

        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def verify_adb(self) -> bool:
        if self.adb_path.exists():
            return True

        self.last_error = (
            "No se encontró adb.exe en:\n"
            f"{self.adb_path}"
        )

        return False

    def verify_device(
        self,
        device_identifier: str,
    ) -> bool:
        try:
            result = self.run_adb(
                device_identifier,
                ["get-state"],
                timeout=10,
            )

        except subprocess.TimeoutExpired:
            self.last_error = (
                "La Meta Quest agotó el tiempo "
                "de conexión ADB."
            )
            return False

        except OSError as error:
            self.last_error = (
                "No fue posible consultar "
                "la Meta Quest:\n"
                f"{error}"
            )
            return False

        if (
            result.returncode == 0
            and result.stdout.strip() == "device"
        ):
            return True

        self.last_error = (
            result.stderr.strip()
            or result.stdout.strip()
            or "La Meta Quest no está disponible por ADB."
        )

        return False

    def wake_device(
        self,
        device_identifier: str,
    ):
        try:
            self.run_adb(
                device_identifier,
                [
                    "shell",
                    "input",
                    "keyevent",
                    "KEYCODE_WAKEUP",
                ],
                timeout=10,
            )

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):
            pass

    def close_previous_dialog(
        self,
        device_identifier: str,
    ):
        try:
            self.run_adb(
                device_identifier,
                [
                    "shell",
                    "am",
                    "force-stop",
                    self.CAST_PACKAGE,
                ],
                timeout=10,
            )

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):
            pass

        time.sleep(0.12)

    def open_casting_dialog(
        self,
        device_identifier: str,
    ) -> bool:
        try:
            result = self.run_adb(
                device_identifier,
                [
                    "shell",
                    "am",
                    "start",
                    "-W",
                    "-a",
                    self.CAST_ACTION,
                    "-n",
                    self.CAST_ACTIVITY,
                ],
                timeout=20,
            )

        except subprocess.TimeoutExpired:
            self.last_error = (
                "La pantalla de transmisión "
                "agotó el tiempo de espera."
            )
            return False

        except OSError as error:
            self.last_error = (
                "No se pudo abrir la pantalla "
                "de transmisión:\n"
                f"{error}"
            )
            return False

        output = (
            f"{result.stdout}\n"
            f"{result.stderr}"
        ).strip()

        lowered_output = output.lower()

        failed = (
            result.returncode != 0
            or "error:" in lowered_output
            or "exception" in lowered_output
            or "unable to resolve" in lowered_output
            or "permission denial" in lowered_output
        )

        if failed:
            self.last_error = (
                output
                or (
                    "Meta rechazó la apertura de "
                    "la pantalla de transmisión."
                )
            )
            return False

        return True

    def dump_ui_xml(
        self,
        device_identifier: str,
    ) -> str:
        try:
            dump_result = self.run_adb(
                device_identifier,
                [
                    "shell",
                    "uiautomator",
                    "dump",
                    "--compressed",
                    self.REMOTE_XML_PATH,
                ],
                timeout=10,
            )

            if dump_result.returncode != 0:
                return ""

            cat_result = self.run_adb(
                device_identifier,
                [
                    "shell",
                    "cat",
                    self.REMOTE_XML_PATH,
                ],
                timeout=10,
            )

            try:
                self.run_adb(
                    device_identifier,
                    [
                        "shell",
                        "rm",
                        self.REMOTE_XML_PATH,
                    ],
                    timeout=5,
                )

            except (
                subprocess.TimeoutExpired,
                OSError,
            ):
                pass

            return cat_result.stdout

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):
            return ""

    @staticmethod
    def normalize_text(
        value: str,
    ) -> str:
        return " ".join(
            value.lower().strip().split()
        )

    @staticmethod
    def parse_bounds(
        bounds_text: str,
    ) -> tuple[int, int] | None:
        match = re.fullmatch(
            r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",
            bounds_text.strip(),
        )

        if not match:
            return None

        left = int(match.group(1))
        top = int(match.group(2))
        right = int(match.group(3))
        bottom = int(match.group(4))

        return (
            (left + right) // 2,
            (top + bottom) // 2,
        )

    @staticmethod
    def find_clickable_parent(node):
        current_node = node

        while current_node is not None:
            if (
                getattr(
                    current_node,
                    "tagName",
                    "",
                )
                == "node"
            ):
                clickable = current_node.getAttribute(
                    "clickable"
                )

                enabled = current_node.getAttribute(
                    "enabled"
                )

                if (
                    clickable == "true"
                    and enabled == "true"
                ):
                    return current_node

            current_node = current_node.parentNode

        return None

    def find_receiver_coordinates(
        self,
        xml_content: str,
        receiver_name: str,
    ) -> tuple[int, int] | None:
        if not xml_content.strip():
            return None

        try:
            document = minidom.parseString(
                xml_content
            )

        except Exception:
            return None

        target_name = self.normalize_text(
            receiver_name
        )

        nodes = document.getElementsByTagName(
            "node"
        )

        for node in nodes:
            text = self.normalize_text(
                node.getAttribute("text")
            )

            description = self.normalize_text(
                node.getAttribute("content-desc")
            )

            combined_text = self.normalize_text(
                f"{text} {description}"
            )

            if target_name not in combined_text:
                continue

            clickable_node = (
                self.find_clickable_parent(node)
            )

            if clickable_node is None:
                continue

            coordinates = self.parse_bounds(
                clickable_node.getAttribute(
                    "bounds"
                )
            )

            if coordinates:
                return coordinates

        return None

    def find_next_button_coordinates(
        self,
        xml_content: str,
    ) -> tuple[int, int] | None:
        if not xml_content.strip():
            return None

        try:
            document = minidom.parseString(
                xml_content
            )

        except Exception:
            return None

        nodes = document.getElementsByTagName(
            "node"
        )

        for node in nodes:
            resource_id = node.getAttribute(
                "resource-id"
            )

            text = self.normalize_text(
                node.getAttribute("text")
            )

            clickable = node.getAttribute(
                "clickable"
            )

            enabled = node.getAttribute(
                "enabled"
            )

            is_next_button = (
                resource_id
                == (
                    "com.oculus.metacam:id/"
                    "oc_dialog_primary_button"
                )
                or text == "siguiente"
                or text == "next"
            )

            if not is_next_button:
                continue

            if (
                clickable != "true"
                or enabled != "true"
            ):
                continue

            coordinates = self.parse_bounds(
                node.getAttribute("bounds")
            )

            if coordinates:
                return coordinates

        return None

    def tap(
        self,
        device_identifier: str,
        x_coordinate: int,
        y_coordinate: int,
    ) -> bool:
        try:
            result = self.run_adb(
                device_identifier,
                [
                    "shell",
                    "input",
                    "tap",
                    str(x_coordinate),
                    str(y_coordinate),
                ],
                timeout=8,
            )

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):
            return False

        return result.returncode == 0

    def start_casting(
        self,
        device_identifier: str,
        receiver_name: str,
    ) -> tuple[bool, str]:
        self.last_error = ""

        device_identifier = (
            device_identifier.strip()
        )

        receiver_name = (
            receiver_name.strip()
        )

        if not device_identifier:
            return (
                False,
                "La Meta Quest no está conectada.",
            )

        if not receiver_name:
            return (
                False,
                "La TV no tiene un nombre Chromecast.",
            )

        if not self.verify_adb():
            return False, self.last_error

        if not self.verify_device(
            device_identifier
        ):
            return False, self.last_error

        self.wake_device(
            device_identifier
        )

        self.close_previous_dialog(
            device_identifier
        )

        if not self.open_casting_dialog(
            device_identifier
        ):
            return False, self.last_error

        # Espera mínima para que aparezca la lista de TVs.
        time.sleep(0.8)

        # Selecciona la TV directamente por coordenadas.
        # Evita UIAutomator, que era la causa principal de la demora.
        receiver_coordinates = (
            self.RECEIVER_FALLBACK_COORDINATES
        )

        receiver_x, receiver_y = (
            receiver_coordinates
        )

        if not self.tap(
            device_identifier,
            receiver_x,
            receiver_y,
        ):
            return (
                False,
                "No se pudo seleccionar la TV.",
            )

        # Espera mínima para que se habilite Siguiente.
        time.sleep(0.5)

        # Pulsa Siguiente directamente por coordenadas.
        next_coordinates = (
            self.NEXT_FALLBACK_COORDINATES
        )

        next_x, next_y = (
            next_coordinates
        )

        if not self.tap(
            device_identifier,
            next_x,
            next_y,
        ):
            return (
                False,
                "No se pudo confirmar la transmisión.",
            )

        time.sleep(0.65)

        return (
            True,
            (
                f"Transmisión iniciada correctamente "
                f"en {receiver_name}."
            ),
        )

    def stop_casting(
        self,
        device_identifier: str,
    ) -> tuple[bool, str]:
        self.last_error = ""

        device_identifier = (
            device_identifier.strip()
        )

        if not device_identifier:
            return (
                False,
                "La Meta Quest no está conectada.",
            )

        if not self.verify_adb():
            return (
                False,
                self.last_error,
            )

        if not self.verify_device(
            device_identifier
        ):
            return (
                False,
                self.last_error,
            )

        try:
            if not self.open_casting_dialog(
                device_identifier
            ):
                return (
                    False,
                    self.last_error
                    or (
                        "No se pudo abrir el control "
                        "de transmisión."
                    ),
                )

            time.sleep(0.30)

            result = self.run_adb(
                device_identifier,
                [
                    "shell",
                    "am",
                    "force-stop",
                    self.CAST_PACKAGE,
                ],
                timeout=10,
            )

            if result.returncode != 0:
                return (
                    False,
                    (
                        result.stderr.strip()
                        or result.stdout.strip()
                        or (
                            "La transmisión se detuvo, "
                            "pero no se pudo cerrar "
                            "la ventana."
                        )
                    ),
                )

            time.sleep(0.15)

            return (
                True,
                "La transmisión fue detenida correctamente.",
            )

        except subprocess.TimeoutExpired:
            return (
                False,
                (
                    "Se agotó el tiempo intentando "
                    "detener la transmisión."
                ),
            )

        except OSError as error:
            return (
                False,
                (
                    "No se pudo detener la transmisión:\n"
                    f"{error}"
                ),
            )