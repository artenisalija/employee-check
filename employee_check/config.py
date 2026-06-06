from __future__ import annotations

import json
import socket
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .paths import config_path


DEFAULT_TCP_PORT = 8765
DEFAULT_DISCOVERY_PORT = 8766
DEFAULT_SAMPLE_SECONDS = 5


@dataclass
class EmployerConfig:
    report_hour: int = 18
    retention_days: int = 30
    tcp_port: int = DEFAULT_TCP_PORT
    discovery_port: int = DEFAULT_DISCOVERY_PORT


@dataclass
class EmployeeConfig:
    employee_name: str = ""
    server_host: str = ""
    server_port: int = DEFAULT_TCP_PORT
    discovery_port: int = DEFAULT_DISCOVERY_PORT
    sample_seconds: int = DEFAULT_SAMPLE_SECONDS
    machine_name: str = ""

    def normalized_machine_name(self) -> str:
        return self.machine_name or socket.gethostname()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_employer_config() -> EmployerConfig:
    data = _load_json(config_path("employer"))
    return EmployerConfig(**{**asdict(EmployerConfig()), **data})


def save_employer_config(config: EmployerConfig) -> None:
    _save_json(config_path("employer"), asdict(config))


def load_employee_config() -> EmployeeConfig:
    data = _load_json(config_path("employee"))
    merged = {**asdict(EmployeeConfig()), **data}
    if not merged.get("machine_name"):
        merged["machine_name"] = socket.gethostname()
    return EmployeeConfig(**merged)


def save_employee_config(config: EmployeeConfig) -> None:
    _save_json(config_path("employee"), asdict(config))

