from dataclasses import dataclass

from services.adb_service import AdbService


@dataclass
class Game:
    name: str
    package: str
    activity: str

    @property
    def component(self) -> str:
        return f"{self.package}/{self.activity}"


class GameManager:
    FRIENDLY_NAMES = {
        "com.downpourinteractive.onward": "Onward",
        "com.beatgames.beatsaber": "Beat Saber",
        "com.mightycoconut.walkaboutminigolf": "Walkabout Mini Golf",
        "com.ILMxLAB.VaderImmortal.ep1": "Vader Immortal",
        "com.CloudheadGames.PistolWhip": "Pistol Whip",
        "com.SchellGames.IExpectYouToDie": "I Expect You To Die",
        "com.resolutiongames.demeo": "Demeo",
    }

    IGNORED_PACKAGES = {
        "com.whatsapp",
        "com.oculus.facebook",
        "com.oculus.accountscenter",
        "com.facebook.arvr.quillplayer",
        "com.oculus.helpcenter",
        "com.meta.curio.toybox",
        "com.oculus.igvr",
        "com.meta.handseducationmodule",
        "com.oculus.vrprivacycheckup",
    }

    IGNORED_PREFIXES = (
        "com.meta.shell.",
        "com.oculus.system",
        "com.android.",
    )

    def __init__(self, adb_service: AdbService):
        self.adb = adb_service

    def get_installed_games(self, serial: str) -> list[Game]:
        packages = self._get_third_party_packages(serial)
        games = []

        for package in packages:
            if self._should_ignore(package):
                continue

            activity = self._find_main_activity(serial, package)

            if not activity:
                continue

            name = self._get_friendly_name(package)

            games.append(
                Game(
                    name=name,
                    package=package,
                    activity=activity,
                )
            )

        return sorted(games, key=lambda game: game.name.lower())

    def _get_third_party_packages(self, serial: str) -> list[str]:
        result = self.adb.run_command(
            "-s",
            serial,
            "shell",
            "pm",
            "list",
            "packages",
            "-3",
        )

        packages = []

        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("package:"):
                packages.append(line.replace("package:", "", 1))

        return packages

    def _find_main_activity(
        self,
        serial: str,
        package: str,
    ) -> str | None:
        result = self.adb.run_command(
            "-s",
            serial,
            "shell",
            "dumpsys",
            "package",
            package,
        )

        lines = result.stdout.splitlines()

        for index, line in enumerate(lines):
            if "android.intent.action.MAIN:" not in line:
                continue

            for candidate in lines[index + 1:index + 12]:
                candidate = candidate.strip()

                if package not in candidate or "/" not in candidate:
                    continue

                component = self._extract_component(
                    candidate,
                    package,
                )

                if component:
                    return component.split("/", 1)[1]

        return None

    @staticmethod
    def _extract_component(
        line: str,
        package: str,
    ) -> str | None:
        start = line.find(package)

        if start == -1:
            return None

        component = line[start:].split()[0]

        if "/" not in component:
            return None

        return component

    def _should_ignore(self, package: str) -> bool:
        if package in self.IGNORED_PACKAGES:
            return True

        return package.startswith(self.IGNORED_PREFIXES)

    def _get_friendly_name(self, package: str) -> str:
        if package in self.FRIENDLY_NAMES:
            return self.FRIENDLY_NAMES[package]

        final_part = package.split(".")[-1]

        return final_part.replace("_", " ").replace("-", " ").title()