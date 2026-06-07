from __future__ import annotations

from collections.abc import Callable
from typing import Any


def start_employee_tray(app: Any) -> object | None:
    return _start_tray(
        "Employee Check",
        [
            ("Show Window", lambda: app.root.after(0, app._show_window_on_main_thread)),
            ("Check Updates", lambda: app.root.after(0, app._check_updates)),
            ("About", lambda: app.root.after(0, app._show_about)),
            ("Check In", lambda: app.root.after(0, app._set_status, "checked_in")),
            ("Lunch", lambda: app.root.after(0, app._set_status, "lunch")),
            ("Meeting", lambda: app.root.after(0, app._set_status, "meeting")),
            ("Check Out", lambda: app.root.after(0, app._set_status, "checked_out")),
        ],
    )


def start_employer_tray(app: Any) -> object | None:
    return _start_tray(
        "Employee Check Employer",
        [
            ("Show Dashboard", lambda: app.root.after(0, app._show_window_on_main_thread)),
            ("Check Updates", lambda: app.root.after(0, app._check_updates)),
            ("About", lambda: app.root.after(0, app._show_about)),
            ("Generate Excel Now", lambda: app.root.after(0, app._generate_report_now)),
            ("Open Reports Folder", lambda: app.root.after(0, app._open_reports_folder)),
        ],
    )


def _start_tray(title: str, menu_items: list[tuple[str, Callable[[], None]]]) -> object | None:
    try:
        from PIL import Image, ImageDraw
        import pystray
    except Exception:
        return None

    def make_action(callback: Callable[[], None]) -> Callable[[object, object], None]:
        def action(_icon: object, _item: object) -> None:
            try:
                callback()
            except Exception:
                pass

        return action

    image = Image.new("RGBA", (64, 64), (36, 94, 79, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill=(255, 255, 255, 255))
    draw.text((20, 23), "EC", fill=(36, 94, 79, 255))

    menu = pystray.Menu(*(pystray.MenuItem(label, make_action(callback)) for label, callback in menu_items))
    icon = pystray.Icon("employee_check", image, title, menu)
    try:
        icon.run_detached()
    except Exception:
        return None
    return icon
