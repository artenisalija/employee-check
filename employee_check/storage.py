from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .models import EmployeeSnapshot


class EmployerStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    machine_name TEXT PRIMARY KEY,
                    employee_name TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_name TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    manual_status TEXT NOT NULL,
                    idle_seconds REAL NOT NULL,
                    idle_band TEXT NOT NULL,
                    active_app TEXT,
                    active_process TEXT,
                    active_title TEXT,
                    active_url TEXT,
                    open_apps_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_machine_time ON snapshots(machine_name, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_time ON snapshots(timestamp)")

    def save_snapshot(self, snapshot: EmployeeSnapshot) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO employees(machine_name, employee_name, first_seen, last_seen)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(machine_name) DO UPDATE SET
                    employee_name = excluded.employee_name,
                    last_seen = excluded.last_seen
                """,
                (snapshot.machine_name, snapshot.employee_name, snapshot.timestamp, snapshot.timestamp),
            )
            conn.execute(
                """
                INSERT INTO snapshots(
                    machine_name, employee_name, timestamp, manual_status, idle_seconds, idle_band,
                    active_app, active_process, active_title, active_url, open_apps_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.machine_name,
                    snapshot.employee_name,
                    snapshot.timestamp,
                    snapshot.manual_status,
                    snapshot.idle_seconds,
                    snapshot.idle_band,
                    snapshot.active_window.app_name,
                    snapshot.active_window.process_name,
                    snapshot.active_window.title,
                    snapshot.active_window.url,
                    json.dumps(snapshot.open_apps, separators=(",", ":")),
                ),
            )

    def latest_snapshots(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*
                FROM snapshots s
                JOIN (
                    SELECT machine_name, MAX(timestamp) AS max_timestamp
                    FROM snapshots
                    GROUP BY machine_name
                ) latest
                ON latest.machine_name = s.machine_name AND latest.max_timestamp = s.timestamp
                ORDER BY s.employee_name COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def snapshots_between(self, start_iso: str, end_iso: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM snapshots
                WHERE timestamp >= ? AND timestamp < ?
                ORDER BY employee_name COLLATE NOCASE, machine_name, timestamp
                """,
                (start_iso, end_iso),
            ).fetchall()
        return [dict(row) for row in rows]

    def purge_older_than(self, retention_days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, retention_days))
        cutoff_iso = cutoff.replace(microsecond=0).isoformat()
        with self.connect() as conn:
            cursor = conn.execute("DELETE FROM snapshots WHERE timestamp < ?", (cutoff_iso,))
            return cursor.rowcount

