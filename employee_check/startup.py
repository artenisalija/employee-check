from __future__ import annotations

import os
import platform
import shlex
import stat
import sys
from pathlib import Path


APP_ID = "com.employeecheck.agent"


def install_startup(role: str) -> Path:
    system = platform.system()
    if system == "Windows":
        return _install_windows(role)
    if system == "Darwin":
        return _install_macos(role)
    if system == "Linux":
        return _install_linux(role)
    raise RuntimeError(f"Unsupported platform: {system}")


def uninstall_startup(role: str) -> Path:
    system = platform.system()
    if system == "Windows":
        path = _windows_startup_path(role)
    elif system == "Darwin":
        path = _macos_launch_agent_path(role)
    elif system == "Linux":
        path = _linux_systemd_user_path(role)
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    if path.exists():
        path.unlink()
    return path


def startup_command(role: str) -> list[str]:
    exe = Path(sys.executable)
    script = Path(sys.argv[0]).resolve()
    if script.suffix.lower() in {".exe", ""} and script.name.lower().startswith("employeecheck"):
        return [str(script), role]
    if platform.system() == "Windows" and exe.name.lower() == "python.exe":
        pythonw = exe.with_name("pythonw.exe")
        if pythonw.exists():
            exe = pythonw
    return [str(exe), "-m", "employee_check", role]


def _install_windows(role: str) -> Path:
    path = _windows_startup_path(role)
    command = " ".join(_quote_windows(part) for part in startup_command(role))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"@echo off\r\nstart \"\" {command}\r\n", encoding="utf-8")
    return path


def _windows_startup_path(role: str) -> Path:
    startup = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return startup / f"EmployeeCheck-{role}.cmd"


def _install_macos(role: str) -> Path:
    path = _macos_launch_agent_path(role)
    args = "\n".join(f"        <string>{_xml_escape(part)}</string>" for part in startup_command(role))
    label = f"{APP_ID}.{role}"
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
{args}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plist, encoding="utf-8")
    return path


def _macos_launch_agent_path(role: str) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{APP_ID}.{role}.plist"


def _install_linux(role: str) -> Path:
    path = _linux_systemd_user_path(role)
    command = " ".join(shlex.quote(part) for part in startup_command(role))
    unit = f"""[Unit]
Description=Employee Check {role}

[Service]
ExecStart={command}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(unit, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IRUSR | stat.S_IWUSR)
    return path


def _linux_systemd_user_path(role: str) -> Path:
    return Path.home() / ".config" / "systemd" / "user" / f"employee-check-{role}.service"


def _quote_windows(value: str) -> str:
    if " " not in value and "\t" not in value and '"' not in value:
        return value
    return '"' + value.replace('"', '\\"') + '"'


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
