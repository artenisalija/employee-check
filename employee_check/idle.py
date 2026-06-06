from __future__ import annotations

import ctypes
import platform
import re
import subprocess


def idle_seconds() -> float:
    system = platform.system()
    if system == "Windows":
        return _windows_idle_seconds()
    if system == "Darwin":
        return _mac_idle_seconds()
    if system == "Linux":
        return _linux_idle_seconds()
    return 0.0


def _windows_idle_seconds() -> float:
    class LastInputInfo(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    last_input = LastInputInfo()
    last_input.cbSize = ctypes.sizeof(last_input)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input)):  # type: ignore[attr-defined]
        return 0.0
    tick_count = ctypes.windll.kernel32.GetTickCount()  # type: ignore[attr-defined]
    elapsed_ms = tick_count - last_input.dwTime
    return max(0.0, elapsed_ms / 1000.0)


def _mac_idle_seconds() -> float:
    try:
        result = subprocess.run(
            ["ioreg", "-c", "IOHIDSystem"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 0.0
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
    if not match:
        return 0.0
    return int(match.group(1)) / 1_000_000_000.0


def _linux_idle_seconds() -> float:
    try:
        result = subprocess.run(
            ["xprintidle"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode == 0:
            return max(0.0, int(result.stdout.strip()) / 1000.0)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return 0.0

