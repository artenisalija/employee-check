from __future__ import annotations

import json
import queue
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
from typing import Any

from . import __version__
from .config import EmployerConfig, load_employer_config, save_employer_config
from .models import (
    STATUSES,
    STATUS_CHECKED_IN,
    STATUS_CHECKED_OUT,
    STATUS_LUNCH,
    STATUS_MEETING,
    EmployeeSnapshot,
)
from .net import DiscoveryResponder, JsonTcpServer
from .paths import config_path, employer_db_path, reports_dir
from .reporting import generate_daily_report
from .startup import install_startup
from .storage import EmployerStore
from .tray import start_employer_tray
from .updates import check_for_update, open_download_page


IDLE_COLORS = {
    "active": "#e6ffed",
    "yellow": "#fefcbf",
    "orange": "#feebc8",
    "red": "#fed7d7",
}

IDLE_BADGE_COLORS = {
    "active": ("#2f855a", "#ffffff"),
    "yellow": ("#f6e05e", "#1a202c"),
    "orange": ("#dd6b20", "#1a202c"),
    "red": ("#c53030", "#ffffff"),
}

STATUS_LABELS = {
    STATUS_CHECKED_IN: "Checked In",
    STATUS_CHECKED_OUT: "Checked Out",
    STATUS_LUNCH: "Lunch",
    STATUS_MEETING: "Meeting",
}


class EmployerApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Employee Check Employer")
        self.root.geometry("1120x700")
        self.root.minsize(900, 560)
        self.first_run = not config_path("employer").exists()
        self.config = load_employer_config()
        self.store = EmployerStore(employer_db_path())
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.snapshots_by_machine: dict[str, dict[str, Any]] = {}
        self.last_report_day = ""
        self.tray_icon = None
        self._ensure_config()
        self._build_ui()
        self._load_latest_snapshots()
        self.tray_icon = start_employer_tray(self)
        self.server = JsonTcpServer("", self.config.tcp_port, self._handle_message)
        self.discovery = DiscoveryResponder(self.config.tcp_port, self.config.discovery_port)
        self.server.start()
        self.discovery.start()
        self.scheduler = threading.Thread(target=self._scheduler_loop, name="report-scheduler", daemon=True)
        self.scheduler.start()
        self.root.after(1000, self._refresh_loop)
        self.root.protocol("WM_DELETE_WINDOW", self._hide_window)

    def _load_latest_snapshots(self) -> None:
        for row in self.store.latest_snapshots():
            row_data = dict(row)
            open_apps = []
            try:
                open_apps = json.loads(row_data.get("open_apps_json") or "[]")
            except json.JSONDecodeError:
                open_apps = []
            try:
                status_totals = json.loads(row_data.get("status_totals_json") or "{}")
            except json.JSONDecodeError:
                status_totals = {}
            self.snapshots_by_machine[row_data["machine_name"]] = {
                "employee_name": row_data["employee_name"],
                "machine_name": row_data["machine_name"],
                "manual_status": row_data["manual_status"],
                "local_timestamp": row_data.get("local_timestamp") or row_data["timestamp"],
                "status_started_at": row_data.get("status_started_at") or "",
                "status_started_at_utc": row_data.get("status_started_at_utc") or "",
                "status_elapsed_seconds": row_data.get("status_elapsed_seconds") or 0,
                "status_totals_seconds": status_totals,
                "status_totals_day": row_data.get("status_totals_day") or "",
                "idle_seconds": row_data["idle_seconds"],
                "idle_band": row_data["idle_band"],
                "active_window": {
                    "app_name": row_data.get("active_app") or "",
                    "process_name": row_data.get("active_process") or "",
                    "title": row_data.get("active_title") or "",
                    "url": row_data.get("active_url") or "",
                    "pid": None,
                },
                "open_apps": open_apps,
                "timestamp": row_data["timestamp"],
            }
        if self.snapshots_by_machine:
            self._render_tree()

    def run(self) -> None:
        self.root.mainloop()

    def _ensure_config(self) -> None:
        changed = False
        if self.first_run:
            report_hour = simpledialog.askinteger(
                "Daily Report",
                "Enter the hour for the daily Excel report (0-23):",
                parent=self.root,
                initialvalue=self.config.report_hour,
                minvalue=0,
                maxvalue=23,
            )
            if report_hour is not None:
                self.config.report_hour = report_hour
                changed = True
            retention_days = simpledialog.askinteger(
                "Data Retention",
                "Enter how many days of monitoring data to keep:",
                parent=self.root,
                initialvalue=self.config.retention_days,
                minvalue=1,
                maxvalue=3650,
            )
            if retention_days is not None:
                self.config.retention_days = retention_days
                changed = True
        if not (0 <= self.config.report_hour <= 23):
            self.config.report_hour = 18
            changed = True
        if self.config.retention_days <= 0:
            self.config.retention_days = 30
            changed = True
        if changed or self.first_run:
            save_employer_config(self.config)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        header = ttk.Frame(self.root, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Employee Check", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        self.server_var = tk.StringVar(value=f"Listening on LAN port {self.config.tcp_port}")
        ttk.Label(header, textvariable=self.server_var).grid(row=1, column=0, sticky="w", pady=(2, 0))
        ttk.Button(header, text="Install Startup", command=self._install_startup).grid(row=0, column=1, sticky="e")
        ttk.Button(header, text="Show Window", command=self._show_window).grid(row=0, column=2, sticky="e", padx=(8, 0))

        controls = ttk.LabelFrame(self.root, text="Settings", padding=12)
        controls.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        for col in range(9):
            controls.columnconfigure(col, weight=0)
        controls.columnconfigure(9, weight=1)
        self.report_hour_var = tk.IntVar(value=self.config.report_hour)
        self.retention_var = tk.IntVar(value=self.config.retention_days)
        ttk.Label(controls, text="Report hour").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(controls, from_=0, to=23, width=5, textvariable=self.report_hour_var).grid(
            row=0, column=1, sticky="w", padx=(8, 16)
        )
        ttk.Label(controls, text="Retention days").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(controls, from_=1, to=3650, width=7, textvariable=self.retention_var).grid(
            row=0, column=3, sticky="w", padx=(8, 16)
        )
        ttk.Button(controls, text="Save", command=self._save_settings).grid(row=0, column=4, sticky="w")
        ttk.Button(controls, text="Generate Excel Now", command=self._generate_report_now).grid(
            row=0, column=5, sticky="w", padx=(8, 0)
        )
        ttk.Button(controls, text="Open Reports Folder", command=self._open_reports_folder).grid(
            row=0, column=6, sticky="w", padx=(8, 0)
        )
        ttk.Button(controls, text="Check Updates", command=self._check_updates).grid(
            row=0, column=7, sticky="w", padx=(8, 0)
        )
        ttk.Button(controls, text="About", command=self._show_about).grid(
            row=0, column=8, sticky="w", padx=(8, 0)
        )

        body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))

        list_frame = ttk.Frame(body)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        columns = ("employee", "machine", "status", "status_time", "idle", "app", "machine_time", "title")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "employee": "Employee",
            "machine": "Machine",
            "status": "Status",
            "status_time": "Status Time",
            "idle": "Idle",
            "app": "Active App",
            "machine_time": "Machine Time",
            "title": "Title / URL",
        }
        widths = {
            "employee": 130,
            "machine": 130,
            "status": 100,
            "status_time": 120,
            "idle": 90,
            "app": 130,
            "machine_time": 150,
            "title": 280,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], minwidth=70, stretch=column == "title")
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll = ttk.Scrollbar(list_frame, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.tag_configure("active", background=IDLE_COLORS["active"])
        self.tree.tag_configure("yellow", background=IDLE_COLORS["yellow"])
        self.tree.tag_configure("orange", background=IDLE_COLORS["orange"])
        self.tree.tag_configure("red", background=IDLE_COLORS["red"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        body.add(list_frame, weight=3)

        detail_frame = ttk.LabelFrame(body, text="Employee Detail", padding=12)
        detail_frame.rowconfigure(11, weight=1)
        detail_frame.columnconfigure(1, weight=1)
        self.detail_vars = {name: tk.StringVar(value="") for name in [
            "employee",
            "machine",
            "status",
            "status_time",
            "status_started",
            "idle",
            "machine_time",
            "active_app",
            "active_title",
            "active_url",
        ]}
        labels = [
            ("Employee", "employee"),
            ("Machine", "machine"),
            ("Status", "status"),
            ("Status Time", "status_time"),
            ("Status Started", "status_started"),
            ("Idle", "idle"),
            ("Machine Time", "machine_time"),
            ("Active App", "active_app"),
            ("Title", "active_title"),
            ("URL", "active_url"),
        ]
        for row, (label, key) in enumerate(labels):
            ttk.Label(detail_frame, text=label).grid(row=row, column=0, sticky="nw", pady=3)
            if key == "idle":
                self.detail_idle_badge = tk.Label(
                    detail_frame,
                    textvariable=self.detail_vars[key],
                    bg=IDLE_BADGE_COLORS["active"][0],
                    fg=IDLE_BADGE_COLORS["active"][1],
                    padx=8,
                    pady=4,
                    anchor="w",
                )
                self.detail_idle_badge.grid(row=row, column=1, sticky="nw", padx=(10, 0), pady=3)
            else:
                ttk.Label(detail_frame, textvariable=self.detail_vars[key], wraplength=320).grid(
                    row=row, column=1, sticky="nw", padx=(10, 0), pady=3
                )
        ttk.Label(detail_frame, text="Status Minutes").grid(row=len(labels), column=0, sticky="nw", pady=(10, 0))
        status_box_frame = ttk.Frame(detail_frame)
        status_box_frame.grid(row=len(labels), column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        status_box_frame.columnconfigure(0, weight=1)
        self.detail_status_totals = tk.Listbox(status_box_frame, height=4)
        self.detail_status_totals.grid(row=0, column=0, sticky="ew")

        ttk.Label(detail_frame, text="Open Apps").grid(row=len(labels) + 1, column=0, sticky="nw", pady=(10, 0))
        apps_box_frame = ttk.Frame(detail_frame)
        apps_box_frame.grid(row=len(labels) + 1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))
        apps_box_frame.rowconfigure(0, weight=1)
        apps_box_frame.columnconfigure(0, weight=1)
        self.detail_apps = tk.Listbox(apps_box_frame)
        self.detail_apps.grid(row=0, column=0, sticky="nsew")
        detail_scroll = ttk.Scrollbar(apps_box_frame, command=self.detail_apps.yview)
        detail_scroll.grid(row=0, column=1, sticky="ns")
        self.detail_apps.configure(yscrollcommand=detail_scroll.set)
        body.add(detail_frame, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(16, 0, 16, 8)).grid(row=3, column=0, sticky="ew")

    def _handle_message(self, message: dict[str, Any], addr: tuple[str, int]) -> dict[str, Any]:
        if message.get("type") != "snapshot":
            return {"ok": False, "error": "unsupported message type"}
        snapshot = EmployeeSnapshot.from_dict(message.get("payload") or {})
        self.store.save_snapshot(snapshot)
        self.events.put(("snapshot", snapshot.to_dict()))
        return {"ok": True, "server_time": datetime.now().isoformat(timespec="seconds")}

    def _refresh_loop(self) -> None:
        updated = False
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "snapshot":
                self.snapshots_by_machine[payload["machine_name"]] = payload
                updated = True
            elif event == "status":
                self.status_var.set(str(payload))
            elif event == "update":
                self._show_update_result(payload)
        if updated:
            self._render_tree()
        self.root.after(1000, self._refresh_loop)

    def _render_tree(self) -> None:
        selected = self._selected_machine()
        existing = set(self.tree.get_children())
        machines = set(self.snapshots_by_machine)
        for item in existing - machines:
            self.tree.delete(item)
        for machine, snapshot in sorted(
            self.snapshots_by_machine.items(),
            key=lambda pair: pair[1].get("employee_name", "").lower(),
        ):
            active = snapshot.get("active_window") or {}
            title_or_url = active.get("url") or active.get("title") or ""
            status_elapsed = float(snapshot.get("status_elapsed_seconds", 0) or 0)
            status = snapshot.get("manual_status", "")
            values = (
                snapshot.get("employee_name", ""),
                snapshot.get("machine_name", ""),
                STATUS_LABELS.get(status, status),
                f"{_format_minutes(status_elapsed)} / {_format_idle(status_elapsed)}",
                f"{_format_idle(float(snapshot.get('idle_seconds', 0)))} / {snapshot.get('idle_band', '')}",
                active.get("app_name") or active.get("process_name") or "",
                _format_machine_time(snapshot.get("local_timestamp") or snapshot.get("timestamp", "")),
                title_or_url,
            )
            band = snapshot.get("idle_band", "active")
            if machine in existing:
                self.tree.item(machine, values=values, tags=(band,))
            else:
                self.tree.insert("", tk.END, iid=machine, values=values, tags=(band,))
        if selected and selected in self.snapshots_by_machine:
            self.tree.selection_set(selected)
            self._render_detail(self.snapshots_by_machine[selected])
        elif self.snapshots_by_machine and not self.tree.selection():
            first = next(iter(sorted(self.snapshots_by_machine)))
            self.tree.selection_set(first)
            self._render_detail(self.snapshots_by_machine[first])

    def _on_select(self, _event=None) -> None:
        machine = self._selected_machine()
        if machine and machine in self.snapshots_by_machine:
            self._render_detail(self.snapshots_by_machine[machine])

    def _render_detail(self, snapshot: dict[str, Any]) -> None:
        active = snapshot.get("active_window") or {}
        status = snapshot.get("manual_status", "")
        status_elapsed = float(snapshot.get("status_elapsed_seconds", 0) or 0)
        self.detail_vars["employee"].set(snapshot.get("employee_name", ""))
        self.detail_vars["machine"].set(snapshot.get("machine_name", ""))
        self.detail_vars["status"].set(STATUS_LABELS.get(status, status))
        self.detail_vars["status_time"].set(f"{_format_minutes(status_elapsed)} / {_format_idle(status_elapsed)}")
        self.detail_vars["status_started"].set(_format_machine_time(snapshot.get("status_started_at") or ""))
        self.detail_vars["idle"].set(
            f"{_format_idle(float(snapshot.get('idle_seconds', 0)))} / {snapshot.get('idle_band', '')}"
        )
        badge_bg, badge_fg = IDLE_BADGE_COLORS.get(snapshot.get("idle_band", "active"), IDLE_BADGE_COLORS["active"])
        self.detail_idle_badge.configure(bg=badge_bg, fg=badge_fg)
        self.detail_vars["machine_time"].set(_format_machine_time(snapshot.get("local_timestamp") or snapshot.get("timestamp", "")))
        self.detail_vars["active_app"].set(active.get("app_name") or active.get("process_name") or "")
        self.detail_vars["active_title"].set(active.get("title") or "")
        self.detail_vars["active_url"].set(active.get("url") or "")
        self.detail_status_totals.delete(0, tk.END)
        totals = _status_totals_from_snapshot(snapshot)
        for total_status in STATUSES:
            self.detail_status_totals.insert(
                tk.END,
                f"{STATUS_LABELS[total_status]}: {_format_minutes(totals.get(total_status, 0.0))}",
            )
        self.detail_apps.delete(0, tk.END)
        for app in snapshot.get("open_apps") or []:
            self.detail_apps.insert(tk.END, app)

    def _selected_machine(self) -> str:
        selected = self.tree.selection()
        return selected[0] if selected else ""

    def _save_settings(self) -> None:
        try:
            report_hour = int(self.report_hour_var.get())
            retention_days = int(self.retention_var.get())
            if not (0 <= report_hour <= 23):
                raise ValueError("Report hour must be between 0 and 23.")
            if retention_days <= 0:
                raise ValueError("Retention days must be positive.")
        except Exception as exc:
            messagebox.showerror("Settings", str(exc))
            return
        self.config.report_hour = report_hour
        self.config.retention_days = retention_days
        save_employer_config(self.config)
        purged = self.store.purge_older_than(retention_days)
        self.status_var.set(f"Settings saved. Purged {purged} old rows.")

    def _generate_report_now(self) -> None:
        try:
            path = generate_daily_report(self.store)
        except Exception as exc:
            messagebox.showerror("Excel Report", f"Could not generate report:\n{exc}")
            return
        self.status_var.set(f"Report generated: {path}")
        messagebox.showinfo("Excel Report", f"Report generated:\n{path}")

    def _open_reports_folder(self) -> None:
        path = reports_dir()
        try:
            import os
            import platform
            import subprocess

            system = platform.system()
            if system == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Reports", f"Could not open reports folder:\n{exc}")

    def _install_startup(self) -> None:
        try:
            path = install_startup("employer")
        except Exception as exc:
            messagebox.showerror("Startup", f"Could not install startup entry:\n{exc}")
            return
        messagebox.showinfo("Startup", f"Startup entry installed:\n{path}")

    def _check_updates(self) -> None:
        threading.Thread(target=self._check_updates_worker, name="employer-update-check", daemon=True).start()

    def _check_updates_worker(self) -> None:
        result = check_for_update()
        self.events.put(("update", result))

    def _show_update_result(self, result) -> None:
        if result.error:
            messagebox.showerror("Updates", f"Could not check for updates:\n{result.error}")
            return
        if result.is_update_available:
            should_open = messagebox.askyesno(
                "Updates",
                f"Version {result.latest_version} is available.\n"
                f"Current version: {result.current_version}\n\n"
                "Open the download page?",
            )
            if should_open:
                open_download_page(result.release_url)
            return
        messagebox.showinfo("Updates", f"Employee Check is up to date.\nVersion: {result.current_version}")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About Employee Check",
            f"Employee Check Employer\n"
            f"Version: {__version__}\n"
            f"Listening port: {self.config.tcp_port}",
        )

    def _hide_window(self) -> None:
        if self.tray_icon:
            self.root.withdraw()
        else:
            self.root.iconify()

    def _show_window(self) -> None:
        self.root.after(0, self._show_window_on_main_thread)

    def _show_window_on_main_thread(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _scheduler_loop(self) -> None:
        while True:
            now = datetime.now().astimezone()
            if now.hour == self.config.report_hour:
                day_key = now.date().isoformat()
                if self.last_report_day != day_key:
                    try:
                        path = generate_daily_report(self.store)
                        self.store.purge_older_than(self.config.retention_days)
                        self.last_report_day = day_key
                        self.events.put(("status", f"Daily report generated: {path}"))
                    except Exception as exc:
                        self.events.put(("status", f"Daily report failed: {exc}"))
            time.sleep(60)


def _format_idle(seconds: float) -> str:
    seconds = int(max(0, seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _format_minutes(seconds: float) -> str:
    return f"{max(0.0, seconds) / 60.0:.1f} min"


def _format_machine_time(value: str) -> str:
    if not value:
        return "unknown"
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def _status_totals_from_snapshot(snapshot: dict[str, Any]) -> dict[str, float]:
    totals = snapshot.get("status_totals_seconds") or {}
    if isinstance(totals, str):
        try:
            totals = json.loads(totals)
        except json.JSONDecodeError:
            totals = {}
    return {str(status): float(seconds or 0) for status, seconds in dict(totals).items()}


def run_employer_app() -> None:
    EmployerApp().run()
