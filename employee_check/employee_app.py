from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .config import EmployeeConfig, load_employee_config, save_employee_config
from .models import STATUS_CHECKED_IN, STATUS_CHECKED_OUT, STATUS_LUNCH, STATUS_MEETING, WireMessage
from .monitor import collect_snapshot
from .net import discover_server, send_json
from .startup import install_startup
from .tray import start_employee_tray


STATUS_LABELS = {
    STATUS_CHECKED_IN: "Checked In",
    STATUS_CHECKED_OUT: "Checked Out",
    STATUS_LUNCH: "Lunch",
    STATUS_MEETING: "Meeting",
}

IDLE_COLORS = {
    "active": "#2f855a",
    "yellow": "#b7791f",
    "orange": "#c05621",
    "red": "#c53030",
}


class EmployeeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Employee Check")
        self.root.geometry("520x420")
        self.root.minsize(460, 360)
        self.config = load_employee_config()
        self.manual_status = STATUS_CHECKED_IN
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
        self.root.rowconfigure(4, weight=1)

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

        connection_frame = ttk.Frame(self.root, padding=(16, 0, 16, 0))
        connection_frame.grid(row=2, column=0, sticky="ew")
        connection_frame.columnconfigure(1, weight=1)
        ttk.Label(connection_frame, text="Employer").grid(row=0, column=0, sticky="w")
        self.server_var = tk.StringVar(value="")
        ttk.Label(connection_frame, textvariable=self.server_var).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(connection_frame, text="Change", command=self._change_server).grid(row=0, column=2, sticky="e")

        live_frame = ttk.LabelFrame(self.root, text="Live", padding=12)
        live_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=8)
        live_frame.columnconfigure(1, weight=1)
        self.idle_var = tk.StringVar(value="Idle: unknown")
        self.active_var = tk.StringVar(value="Active app: unknown")
        self.title_var = tk.StringVar(value="Title/URL: unknown")
        ttk.Label(live_frame, textvariable=self.idle_var).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(live_frame, textvariable=self.active_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(live_frame, textvariable=self.title_var, wraplength=470).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        apps_frame = ttk.LabelFrame(self.root, text="Open Apps", padding=12)
        apps_frame.grid(row=4, column=0, sticky="nsew", padx=16, pady=(8, 16))
        apps_frame.rowconfigure(0, weight=1)
        apps_frame.columnconfigure(0, weight=1)
        self.apps_list = tk.Listbox(apps_frame, height=6)
        self.apps_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(apps_frame, command=self.apps_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.apps_list.configure(yscrollcommand=scrollbar.set)

        footer = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        footer.grid(row=5, column=0, sticky="ew")
        ttk.Button(footer, text="Install Startup", command=self._install_startup).grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Show Window", command=self._show_window).grid(row=0, column=1, sticky="w", padx=(8, 0))

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
        self.manual_status = status
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
                snapshot = collect_snapshot(
                    self.config.employee_name,
                    self.config.normalized_machine_name(),
                    self.manual_status,
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
        self.root.after(500, self._drain_events)

    def _render_snapshot(self, snapshot) -> None:
        self._refresh_identity_labels()
        idle_text = _format_idle(snapshot.idle_seconds)
        self.idle_var.set(f"Idle: {idle_text} ({snapshot.idle_band})")
        active = snapshot.active_window.app_name or snapshot.active_window.process_name or "unknown"
        self.active_var.set(f"Active app: {active}")
        title_or_url = snapshot.active_window.url or snapshot.active_window.title or "unknown"
        self.title_var.set(f"Title/URL: {title_or_url}")
        self.apps_list.delete(0, tk.END)
        for app in snapshot.open_apps:
            self.apps_list.insert(tk.END, app)
        if snapshot.idle_band == "red" and self.manual_status == STATUS_CHECKED_IN:
            self.root.bell()


def _format_idle(seconds: float) -> str:
    seconds = int(max(0, seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def run_employee_app() -> None:
    EmployeeApp().run()
