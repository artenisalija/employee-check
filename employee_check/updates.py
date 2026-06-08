from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import urllib.request
import webbrowser
from dataclasses import dataclass

from . import __version__


RELEASES_URL = "https://github.com/artenisalija/employee-check/releases/latest"
LATEST_RELEASE_API = "https://api.github.com/repos/artenisalija/employee-check/releases/latest"


@dataclass
class UpdateResult:
    current_version: str
    latest_version: str = ""
    release_url: str = RELEASES_URL
    is_update_available: bool = False
    error: str = ""


def check_for_update() -> UpdateResult:
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={"User-Agent": f"EmployeeCheck/{__version__}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return UpdateResult(current_version=__version__, error=str(exc))

    latest = str(data.get("tag_name") or "").lstrip("v")
    release_url = str(data.get("html_url") or RELEASES_URL)
    return UpdateResult(
        current_version=__version__,
        latest_version=latest,
        release_url=release_url,
        is_update_available=_version_tuple(latest) > _version_tuple(__version__),
    )


def open_download_page(url: str = RELEASES_URL) -> bool:
    system = platform.system()
    if system == "Windows":
        try:
            os.startfile(url)  # type: ignore[attr-defined]
            return True
        except Exception:
            pass

    for command in _platform_open_commands(system, url):
        executable = command[0]
        if not shutil.which(executable):
            continue
        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception:
            continue

    try:
        return bool(webbrowser.open(url, new=2))
    except Exception:
        return False


def _platform_open_commands(system: str, url: str) -> list[list[str]]:
    if system == "Linux":
        return [
            ["xdg-open", url],
            ["gio", "open", url],
            ["kde-open5", url],
            ["kde-open", url],
            ["gnome-open", url],
        ]
    if system == "Darwin":
        return [["open", url]]
    return []


def _version_tuple(value: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value)
    return tuple(int(part) for part in parts) if parts else (0,)
