from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


STATUS_CHECKED_IN = "checked_in"
STATUS_CHECKED_OUT = "checked_out"
STATUS_LUNCH = "lunch"
STATUS_MEETING = "meeting"
STATUSES = [STATUS_CHECKED_IN, STATUS_CHECKED_OUT, STATUS_LUNCH, STATUS_MEETING]

IDLE_ACTIVE = "active"
IDLE_YELLOW = "yellow"
IDLE_ORANGE = "orange"
IDLE_RED = "red"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def now_local_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def idle_band(idle_seconds: float) -> str:
    if idle_seconds >= 600:
        return IDLE_RED
    if idle_seconds >= 300:
        return IDLE_ORANGE
    if idle_seconds >= 120:
        return IDLE_YELLOW
    return IDLE_ACTIVE


@dataclass
class ActiveWindow:
    app_name: str = ""
    process_name: str = ""
    pid: int | None = None
    title: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmployeeSnapshot:
    employee_name: str
    machine_name: str
    manual_status: str = STATUS_CHECKED_IN
    idle_seconds: float = 0
    idle_band: str = IDLE_ACTIVE
    active_window: ActiveWindow = field(default_factory=ActiveWindow)
    open_apps: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=now_utc_iso)
    local_timestamp: str = field(default_factory=now_local_iso)
    status_started_at: str = ""
    status_started_at_utc: str = ""
    status_elapsed_seconds: float = 0
    status_totals_seconds: dict[str, float] = field(default_factory=dict)
    status_totals_day: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["active_window"] = self.active_window.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmployeeSnapshot":
        active = data.get("active_window") or {}
        return cls(
            employee_name=str(data.get("employee_name", "")),
            machine_name=str(data.get("machine_name", "")),
            manual_status=str(data.get("manual_status", STATUS_CHECKED_IN)),
            idle_seconds=float(data.get("idle_seconds", 0) or 0),
            idle_band=str(data.get("idle_band", IDLE_ACTIVE)),
            active_window=ActiveWindow(
                app_name=str(active.get("app_name", "")),
                process_name=str(active.get("process_name", "")),
                pid=active.get("pid"),
                title=str(active.get("title", "")),
                url=str(active.get("url", "")),
            ),
            open_apps=list(data.get("open_apps") or []),
            timestamp=str(data.get("timestamp") or now_utc_iso()),
            local_timestamp=str(data.get("local_timestamp") or now_local_iso()),
            status_started_at=str(data.get("status_started_at") or ""),
            status_started_at_utc=str(data.get("status_started_at_utc") or ""),
            status_elapsed_seconds=float(data.get("status_elapsed_seconds", 0) or 0),
            status_totals_seconds={
                str(key): float(value or 0)
                for key, value in (data.get("status_totals_seconds") or {}).items()
            },
            status_totals_day=str(data.get("status_totals_day") or ""),
        )


@dataclass
class WireMessage:
    type: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "payload": self.payload}
