from __future__ import annotations

import ctypes
import ctypes.util
import platform
import re
import subprocess
import time


_last_activity_signature: str | None = None
_last_activity_monotonic = time.monotonic()
_zero_native_signature: str | None = None
_zero_native_start: float | None = None
_ZERO_NATIVE_GRACE_SECONDS = 10.0


def idle_seconds(activity_signature: str | None = None) -> float:
    native = _native_idle_seconds()
    if native is not None:
        if native <= 0.5:
            zero_fallback = _native_zero_fallback_seconds(native, activity_signature)
            if zero_fallback is not None:
                return zero_fallback
            return native
        _reset_native_zero_tracker()
        _sync_fallback_clock(native)
        return native
    return _fallback_idle_seconds(activity_signature)


def _native_idle_seconds() -> float | None:
    system = platform.system()
    if system == "Windows":
        return _windows_idle_seconds()
    if system == "Darwin":
        return _mac_idle_seconds()
    if system == "Linux":
        return _linux_idle_seconds()
    return None


def _windows_idle_seconds() -> float | None:
    class LastInputInfo(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    last_input = LastInputInfo()
    last_input.cbSize = ctypes.sizeof(last_input)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input)):  # type: ignore[attr-defined]
        return None
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    if hasattr(kernel32, "GetTickCount64"):
        kernel32.GetTickCount64.restype = ctypes.c_ulonglong
        tick_count = kernel32.GetTickCount64()
    else:
        tick_count = kernel32.GetTickCount()
    elapsed_ms = tick_count - last_input.dwTime
    return max(0.0, elapsed_ms / 1000.0)


def _mac_idle_seconds() -> float | None:
    try:
        result = subprocess.run(
            ["ioreg", "-c", "IOHIDSystem"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
    if not match:
        return None
    return int(match.group(1)) / 1_000_000_000.0


def _linux_idle_seconds() -> float | None:
    xss_idle = _linux_xss_idle_seconds()
    if xss_idle is not None:
        return xss_idle
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
    return None


def _linux_xss_idle_seconds() -> float | None:
    x11_path = ctypes.util.find_library("X11")
    xss_path = ctypes.util.find_library("Xss")
    if not x11_path or not xss_path:
        return None

    class XScreenSaverInfo(ctypes.Structure):
        _fields_ = [
            ("window", ctypes.c_ulong),
            ("state", ctypes.c_int),
            ("kind", ctypes.c_int),
            ("since", ctypes.c_ulong),
            ("idle", ctypes.c_ulong),
            ("event_mask", ctypes.c_ulong),
        ]

    try:
        x11 = ctypes.cdll.LoadLibrary(x11_path)
        xss = ctypes.cdll.LoadLibrary(xss_path)
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = ctypes.c_void_p
        x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        x11.XDefaultRootWindow.restype = ctypes.c_ulong
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        x11.XFree.argtypes = [ctypes.c_void_p]
        xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
        xss.XScreenSaverQueryInfo.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(XScreenSaverInfo)]
        xss.XScreenSaverQueryInfo.restype = ctypes.c_int

        display = x11.XOpenDisplay(None)
        if not display:
            return None
        info = xss.XScreenSaverAllocInfo()
        if not info:
            x11.XCloseDisplay(display)
            return None
        try:
            root = x11.XDefaultRootWindow(display)
            if not xss.XScreenSaverQueryInfo(display, root, info):
                return None
            return max(0.0, float(info.contents.idle) / 1000.0)
        finally:
            x11.XFree(info)
            x11.XCloseDisplay(display)
    except Exception:
        return None


def _sync_fallback_clock(native_idle_seconds: float) -> None:
    global _last_activity_monotonic
    _last_activity_monotonic = time.monotonic() - max(0.0, native_idle_seconds)


def _fallback_idle_seconds(activity_signature: str | None) -> float:
    global _last_activity_signature, _last_activity_monotonic
    now = time.monotonic()
    if activity_signature and activity_signature != _last_activity_signature:
        _last_activity_signature = activity_signature
        _last_activity_monotonic = now
    return max(0.0, now - _last_activity_monotonic)


def _native_zero_fallback_seconds(native_idle_seconds: float, activity_signature: str | None) -> float | None:
    global _zero_native_signature, _zero_native_start, _last_activity_signature, _last_activity_monotonic
    signature = activity_signature or ""
    now = time.monotonic()
    if signature != _zero_native_signature:
        _zero_native_signature = signature
        _zero_native_start = now
        _last_activity_signature = signature
        _last_activity_monotonic = now
        return None

    if _zero_native_start is None:
        _zero_native_start = now
        return None

    elapsed = now - _zero_native_start
    if elapsed < _ZERO_NATIVE_GRACE_SECONDS:
        return None
    return max(0.0, elapsed)


def _reset_native_zero_tracker() -> None:
    global _zero_native_signature, _zero_native_start
    _zero_native_signature = None
    _zero_native_start = None
