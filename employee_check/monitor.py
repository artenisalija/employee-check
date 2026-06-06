from __future__ import annotations

import ctypes
import platform
import subprocess
from pathlib import Path

import psutil

from .idle import idle_seconds
from .models import ActiveWindow, EmployeeSnapshot, idle_band


BROWSER_APPS = {
    "chrome",
    "google chrome",
    "msedge",
    "microsoft edge",
    "edge",
    "safari",
    "firefox",
    "brave browser",
    "brave",
}


def collect_snapshot(employee_name: str, machine_name: str, manual_status: str) -> EmployeeSnapshot:
    idle = idle_seconds()
    return EmployeeSnapshot(
        employee_name=employee_name,
        machine_name=machine_name,
        manual_status=manual_status,
        idle_seconds=idle,
        idle_band=idle_band(idle),
        active_window=get_active_window(),
        open_apps=list_open_apps(),
    )


def list_open_apps(limit: int = 250) -> list[str]:
    names: set[str] = set()
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            name = proc.info.get("name") or ""
            if not name and proc.info.get("exe"):
                name = Path(proc.info["exe"]).name
            name = name.strip()
            if name:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return sorted(names, key=str.lower)[:limit]


def get_active_window() -> ActiveWindow:
    system = platform.system()
    if system == "Windows":
        return _windows_active_window()
    if system == "Darwin":
        return _mac_active_window()
    if system == "Linux":
        return _linux_active_window()
    return ActiveWindow()


def _windows_active_window() -> ActiveWindow:
    user32 = ctypes.windll.user32  # type: ignore[attr-defined]
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ActiveWindow()

    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    title = buffer.value

    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_name = ""
    app_name = ""
    try:
        proc = psutil.Process(pid.value)
        process_name = proc.name()
        app_name = Path(proc.exe()).stem if proc.exe() else process_name
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        app_name = process_name

    return ActiveWindow(
        app_name=app_name or process_name,
        process_name=process_name,
        pid=int(pid.value) if pid.value else None,
        title=title,
        url="",
    )


def _run_osascript(script: str, timeout: float = 3.0) -> str:
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _mac_active_window() -> ActiveWindow:
    app = _run_osascript('tell application "System Events" to get name of first application process whose frontmost is true')
    title = _run_osascript(
        'tell application "System Events" to tell first application process whose frontmost is true '
        'to if exists window 1 then get name of window 1 else get ""'
    )
    url = ""
    normalized = app.lower()
    if normalized == "safari":
        url = _run_osascript('tell application "Safari" to if exists front document then get URL of front document else get ""')
    elif normalized in {"google chrome", "microsoft edge", "brave browser"}:
        url = _run_osascript(f'tell application "{app}" to if exists front window then get URL of active tab of front window else get ""')

    return ActiveWindow(app_name=app, process_name=app, title=title, url=url)


def _linux_active_window() -> ActiveWindow:
    window_id = _run_cmd(["xdotool", "getactivewindow"])
    if not window_id:
        return ActiveWindow()
    title = _run_cmd(["xdotool", "getwindowname", window_id])
    pid_text = _run_cmd(["xdotool", "getwindowpid", window_id])
    pid: int | None = None
    process_name = ""
    app_name = ""
    if pid_text:
        try:
            pid = int(pid_text)
            proc = psutil.Process(pid)
            process_name = proc.name()
            app_name = Path(proc.exe()).stem if proc.exe() else process_name
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
    return ActiveWindow(app_name=app_name or process_name, process_name=process_name, pid=pid, title=title)


def _run_cmd(args: list[str], timeout: float = 2.0) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

