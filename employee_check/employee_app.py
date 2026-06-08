from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox, simpledialog, ttk

from . import __version__
from .config import EmployeeConfig, load_employee_config, save_employee_config
from .models import (
    STATUSES,
    STATUS_CHECKED_IN,
    STATUS_CHECKED_OUT,
    STATUS_LUNCH,
    STATUS_MEETING,
    WireMessage,
)
from .idle import reset_idle_clock
from .monitor import collect_snapshot
from .net import discover_server, send_json
from .startup import install_startup
from .tray import start_employee_tray
from .updates import check_for_update, open_download_page


STATUS_LABELS = {
    STATUS_CHECKED_IN: "Checked In",
    STATUS_CHECKED_OUT: "Checked Out",
    STATUS_LUNCH: "Lunch",
    STATUS_MEETING: "Meeting",
}

IDLE_COLORS = {
    "active": "#2f855a",
    "yellow": "#f6e05e",
    "orange": "#dd6b20",
    "red": "#c53030",
}

IDLE_FOREGROUNDS = {
    "active": "#ffffff",
    "yellow": "#1a202c",
    "orange": "#1a202c",
    "red": "#ffffff",
}


class EmployeeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Employee Check")
        self.root.geometry("560x560")
        self.root.minsize(500, 460)
        self.config = load_employee_config()
        self.manual_status = STATUS_CHECKED_IN
        self.status_lock = threading.Lock()
        self.status_started_monotonic = time.monotonic()
        self.status_started_local = _now_local_iso()
        self.status_started_utc = _now_utc_iso()
        self.status_totals_day = _local_day()
        self.status_totals_seconds = {status: 0.0 for status in STATUSES}
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.stop_event = threading.Event()
        self.last_snapshot = None
        self.connection_state = "Not connected"
        self.tray_icon = None
        self._build_ui()
        self._ensure_config()
        self.tray_icon = start_employee_tray(self)
        self.worker = threading.Thread(target=self._worker_loop, name="employee-monitor", daemon=True)
        self.worker.start()
        self.root.after(500, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._hide_window)

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

        header = ttk.Frame(self.root, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Employee Check", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        self.employee_label = ttk.Label(header, text="")
        self.employee_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        status_frame = ttk.LabelFrame(self.root, text="Status", padding=12)
        status_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        for col in range(4):
            status_frame.columnconfigure(col, weight=1)
        self.status_var = tk.StringVar(value=STATUS_LABELS[self.manual_status])
        buttons = [
            ("Check In", STATUS_CHECKED_IN),
            ("Check Out", STATUS_CHECKED_OUT),
            ("Lunch", STATUS_LUNCH),
            ("Meeting", STATUS_MEETING),
        ]
        for col, (label, status) in enumerate(buttons):
            ttk.Button(status_frame, text=label, command=lambda value=status: self._set_status(value)).grid(
                row=0, column=col, sticky="ew", padx=4
            )
        ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 11, "bold")).grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(10, 0)
        )

        time_frame = ttk.LabelFrame(self.root, text="Status Time", padding=12)
        time_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        for col in range(4):
            time_frame.columnconfigure(col, weight=1)
        self.status_elapsed_var = tk.StringVar(value="Current: 0.0 min")
        self.machine_time_var = tk.StringVar(value="Machine time: unknown")
        ttk.Label(time_frame, textvariable=self.status_elapsed_var, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(time_frame, textvariable=self.machine_time_var).grid(row=0, column=2, columnspan=2, sticky="e")
        self.status_total_vars = {
            status: tk.StringVar(value=f"{STATUS_LABELS[status]}: 0.0 min")
            for status in STATUSES
        }
        for index, status in enumerate(STATUSES):
            ttk.Label(time_frame, textvariable=self.status_total_vars[status]).grid(
                row=1 + index // 2,
                column=(index % 2) * 2,
                columnspan=2,
                sticky="w",
                pady=(6, 0),
            )

        connection_frame = ttk.Frame(self.root, padding=(16, 0, 16, 0))
        connection_frame.grid(row=3, column=0, sticky="ew")
        connection_frame.columnconfigure(1, weight=1)
        ttk.Label(connection_frame, text="Employer").grid(row=0, column=0, sticky="w")
        self.server_var = tk.StringVar(value="")
        ttk.Label(connection_frame, textvariable=self.server_var).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(connection_frame, text="Change", command=self._change_server).grid(row=0, column=2, sticky="e")

        live_frame = ttk.LabelFrame(self.root, text="Live", padding=12)
        live_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=8)
        live_frame.columnconfigure(1, weight=1)
        self.idle_var = tk.StringVar(value="Idle: unknown")
        self.active_var = tk.StringVar(value="Active app: unknown")
        self.title_var = tk.StringVar(value="Title/URL: unknown")
        self.idle_badge = tk.Label(
            live_frame,
            textvariable=self.idle_var,
            bg=IDLE_COLORS["active"],
            fg=IDLE_FOREGROUNDS["active"],
            padx=8,
            pady=4,
            anchor="w",
        )
        self.idle_badge.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(live_frame, textvariable=self.active_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(live_frame, textvariable=self.title_var, wraplength=470).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        apps_frame = ttk.LabelFrame(self.root, text="Open Apps", padding=12)
        apps_frame.grid(row=5, column=0, sticky="nsew", padx=16, pady=(8, 16))
        apps_frame.rowconfigure(0, weight=1)
        apps_frame.columnconfigure(0, weight=1)
        self.apps_list = tk.Listbox(apps_frame, height=6)
        self.apps_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(apps_frame, command=self.apps_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.apps_list.configure(yscrollcommand=scrollbar.set)

        footer = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        footer.grid(row=6, column=0, sticky="ew")
        ttk.Button(footer, text="Install Startup", command=self._install_startup).grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Show Window", command=self._show_window).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(footer, text="Check Updates", command=self._check_updates).grid(row=0, column=2, sticky="w", padx=(8, 0))
        ttk.Button(footer, text="About", command=self._show_about).grid(row=0, column=3, sticky="w", padx=(8, 0))

    def _ensure_config(self) -> None:
        changed = False
        if not self.config.employee_name:
            name = simpledialog.askstring("Employee Name", "Enter this employee's full name:", parent=self.root)
            if not name:
                name = self.config.normalized_machine_name()
            self.config.employee_name = name.strip()
            changed = True

        if not self.config.server_host:
            discovered = discover_server(self.config.discovery_port)
            if discovered:
                self.config.server_host, self.config.server_port = discovered
                changed = True
            else:
                host = simpledialog.askstring(
                    "Employer Machine",
                    "Enter employer machine IP/hostname:",
                    parent=self.root,
                )
                if host:
                    self.config.server_host = host.strip()
                    changed = True
        if changed:
            save_employee_config(self.config)
        self._refresh_identity_labels()

    def _refresh_identity_labels(self) -> None:
        self.employee_label.configure(
            text=f"{self.config.employee_name} on {self.config.normalized_machine_name()}"
        )
        host = self.config.server_host or "not set"
        self.server_var.set(f"{host}:{self.config.server_port} - {self.connection_state}")

    def _set_status(self, status: str) -> None:
        with self.status_lock:
            self._rollover_status_day_locked()
            now = time.monotonic()
            previous_elapsed = max(0.0, now - self.status_started_monotonic)
            self.status_totals_seconds[self.manual_status] += previous_elapsed
            self.manual_status = status
            self.status_started_monotonic = now
            self.status_started_local = _now_local_iso()
            self.status_started_utc = _now_utc_iso()
            reset_idle_clock()
        self.status_var.set(STATUS_LABELS.get(status, status))

    def _change_server(self) -> None:
        host = simpledialog.askstring(
            "Employer Machine",
            "Enter employer machine IP/hostname:",
            initialvalue=self.config.server_host,
            parent=self.root,
        )
        if host:
            self.config.server_host = host.strip()
            save_employee_config(self.config)
            self._refresh_identity_labels()

    def _install_startup(self) -> None:
        try:
            path = install_startup("employee")
        except Exception as exc:
            messagebox.showerror("Startup", f"Could not install startup entry:\n{exc}")
            return
        messagebox.showinfo("Startup", f"Startup entry installed:\n{path}")

    def _check_updates(self) -> None:
        threading.Thread(target=self._check_updates_worker, name="employee-update-check", daemon=True).start()

    def _check_updates_worker(self) -> None:
        result = check_for_update()
        self.events.put(("update", result))

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

    def _worker_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                timing = self._status_timing_snapshot()
                snapshot = collect_snapshot(
                    self.config.employee_name,
                    self.config.normalized_machine_name(),
                    timing["manual_status"],
                    status_started_at=timing["status_started_at"],
                    status_started_at_utc=timing["status_started_at_utc"],
                    status_elapsed_seconds=timing["status_elapsed_seconds"],
                    status_totals_seconds=timing["status_totals_seconds"],
                    status_totals_day=timing["status_totals_day"],
                )
                self.last_snapshot = snapshot
                response = {}
                if self.config.server_host:
                    response = send_json(
                        self.config.server_host,
                        self.config.server_port,
                        WireMessage("snapshot", snapshot.to_dict()),
                        timeout=4,
                    )
                connected = bool(response.get("ok"))
                self.connection_state = "Connected" if connected else "Not connected"
                self.events.put(("snapshot", snapshot))
            except Exception as exc:
                self.connection_state = f"Error: {exc}"
                self.events.put(("connection", self.connection_state))
            time.sleep(max(2, self.config.sample_seconds))

    def _status_timing_snapshot(self) -> dict[str, object]:
        with self.status_lock:
            self._rollover_status_day_locked()
            elapsed = max(0.0, time.monotonic() - self.status_started_monotonic)
            totals = {status: float(self.status_totals_seconds.get(status, 0.0)) for status in STATUSES}
            totals[self.manual_status] = totals.get(self.manual_status, 0.0) + elapsed
            return {
                "manual_status": self.manual_status,
                "status_started_at": self.status_started_local,
                "status_started_at_utc": self.status_started_utc,
                "status_elapsed_seconds": elapsed,
                "status_totals_seconds": totals,
                "status_totals_day": self.status_totals_day,
            }

    def _rollover_status_day_locked(self) -> None:
        today = _local_day()
        if today == self.status_totals_day:
            return
        self.status_totals_day = today
        self.status_totals_seconds = {status: 0.0 for status in STATUSES}
        self.status_started_monotonic = time.monotonic()
        self.status_started_local = _now_local_iso()
        self.status_started_utc = _now_utc_iso()

    def _drain_events(self) -> None:
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "snapshot":
                self._render_snapshot(payload)
            elif event == "connection":
                self._refresh_identity_labels()
            elif event == "update":
                self._show_update_result(payload)
        self.root.after(500, self._drain_events)

    def _render_snapshot(self, snapshot) -> None:
        self._refresh_identity_labels()
        self.status_var.set(
            f"{STATUS_LABELS.get(snapshot.manual_status, snapshot.manual_status)} since "
            f"{_format_machine_time(snapshot.status_started_at)}"
        )
        self.status_elapsed_var.set(
            f"Current: {_format_minutes(snapshot.status_elapsed_seconds)} "
            f"({_format_idle(snapshot.status_elapsed_seconds)})"
        )
        self.machine_time_var.set(f"Machine time: {_format_machine_time(snapshot.local_timestamp)}")
        for status in STATUSES:
            total = snapshot.status_totals_seconds.get(status, 0.0)
            self.status_total_vars[status].set(f"{STATUS_LABELS[status]}: {_format_minutes(total)}")
        if _status_pauses_idle(snapshot.manual_status):
            self.idle_var.set(f"Idle: paused during {STATUS_LABELS.get(snapshot.manual_status, snapshot.manual_status)}")
        else:
            idle_text = _format_idle(snapshot.idle_seconds)
            self.idle_var.set(f"Idle: {idle_text} ({snapshot.idle_band})")
        self.idle_badge.configure(
            bg=IDLE_COLORS.get(snapshot.idle_band, IDLE_COLORS["active"]),
            fg=IDLE_FOREGROUNDS.get(snapshot.idle_band, IDLE_FOREGROUNDS["active"]),
        )
        active = snapshot.active_window.app_name or snapshot.active_window.process_name or "unknown"
        self.active_var.set(f"Active app: {active}")
        title_or_url = snapshot.active_window.url or snapshot.active_window.title or "unknown"
        self.title_var.set(f"Title/URL: {title_or_url}")
        self.apps_list.delete(0, tk.END)
        for app in snapshot.open_apps:
            self.apps_list.insert(tk.END, app)
        if snapshot.idle_band == "red" and self.manual_status == STATUS_CHECKED_IN:
            self.root.bell()

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
            f"Employee Check Employee\n"
            f"Version: {__version__}\n"
            f"Machine: {self.config.normalized_machine_name()}",
        )


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


def _now_local_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _local_day() -> str:
    return datetime.now().astimezone().date().isoformat()


def _status_pauses_idle(status: str) -> bool:
    return status in {STATUS_LUNCH, STATUS_MEETING}


def run_employee_app() -> None:
    EmployeeApp().run()
