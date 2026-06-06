from __future__ import annotations

import json
import socket
import threading
import time
from collections.abc import Callable
from contextlib import closing
from typing import Any

from .config import DEFAULT_DISCOVERY_PORT, DEFAULT_TCP_PORT
from .models import WireMessage


DISCOVERY_REQUEST = b"EMPLOYEE_CHECK_DISCOVER_V1"
DISCOVERY_RESPONSE_PREFIX = "EMPLOYEE_CHECK_SERVER_V1"


def send_json(host: str, port: int, message: WireMessage, timeout: float = 5.0) -> dict[str, Any]:
    data = (json.dumps(message.to_dict(), separators=(",", ":")) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(data)
        sock.shutdown(socket.SHUT_WR)
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    if not chunks:
        return {}
    try:
        return json.loads(b"".join(chunks).decode("utf-8"))
    except json.JSONDecodeError:
        return {}


class JsonTcpServer:
    def __init__(
        self,
        host: str,
        port: int,
        handler: Callable[[dict[str, Any], tuple[str, int]], dict[str, Any]],
    ) -> None:
        self.host = host
        self.port = port
        self.handler = handler
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._sock: socket.socket | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._serve, name="json-tcp-server", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass

    def _serve(self) -> None:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            self._sock = sock
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(50)
            sock.settimeout(1)
            while not self._stop.is_set():
                try:
                    client, addr = sock.accept()
                except TimeoutError:
                    continue
                except OSError:
                    break
                threading.Thread(
                    target=self._handle_client,
                    args=(client, addr),
                    name=f"json-client-{addr[0]}",
                    daemon=True,
                ).start()

    def _handle_client(self, client: socket.socket, addr: tuple[str, int]) -> None:
        with closing(client) as sock:
            try:
                sock.settimeout(10)
                data = bytearray()
                while True:
                    chunk = sock.recv(65536)
                    if not chunk:
                        break
                    data.extend(chunk)
                    if b"\n" in chunk:
                        break
                request = json.loads(data.decode("utf-8").strip())
                response = self.handler(request, addr)
            except Exception as exc:
                response = {"ok": False, "error": str(exc)}
            try:
                sock.sendall(json.dumps(response, separators=(",", ":")).encode("utf-8"))
            except OSError:
                pass


class DiscoveryResponder:
    def __init__(self, tcp_port: int = DEFAULT_TCP_PORT, discovery_port: int = DEFAULT_DISCOVERY_PORT) -> None:
        self.tcp_port = tcp_port
        self.discovery_port = discovery_port
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._sock: socket.socket | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._serve, name="discovery-responder", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass

    def _serve(self) -> None:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            self._sock = sock
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", self.discovery_port))
            sock.settimeout(1)
            while not self._stop.is_set():
                try:
                    data, addr = sock.recvfrom(1024)
                except TimeoutError:
                    continue
                except OSError:
                    break
                if data != DISCOVERY_REQUEST:
                    continue
                response = f"{DISCOVERY_RESPONSE_PREFIX}|{socket.gethostname()}|{self.tcp_port}".encode("utf-8")
                try:
                    sock.sendto(response, addr)
                except OSError:
                    pass


def discover_server(discovery_port: int = DEFAULT_DISCOVERY_PORT, timeout_seconds: float = 3.0) -> tuple[str, int] | None:
    deadline = time.monotonic() + timeout_seconds
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.5)
        try:
            sock.sendto(DISCOVERY_REQUEST, ("255.255.255.255", discovery_port))
        except OSError:
            return None
        while time.monotonic() < deadline:
            try:
                data, addr = sock.recvfrom(1024)
            except TimeoutError:
                continue
            except OSError:
                return None
            text = data.decode("utf-8", errors="ignore")
            parts = text.split("|")
            if len(parts) == 3 and parts[0] == DISCOVERY_RESPONSE_PREFIX:
                try:
                    return addr[0], int(parts[2])
                except ValueError:
                    return None
    return None

