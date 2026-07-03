"""Unix-socket daemon that keeps the embedder and index warm across queries."""

from __future__ import annotations

import json
import os
import signal
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from whatwasit.config import Config
from whatwasit.embedder import build_embedder
from whatwasit.index import build_index
from whatwasit.models import Command, SearchResult, Session
from whatwasit.brand import CLI_NAME, LEGACY_SOCKET_FILENAME, PID_FILENAME, SOCKET_FILENAME
from whatwasit.search import search

_CONNECT_TIMEOUT = 0.2
_REQUEST_TIMEOUT = 30.0
_MAX_REQUEST_BYTES = 1_048_576


def _xdg_runtime_dir() -> Optional[Path]:
    env = os.environ.get("XDG_RUNTIME_DIR")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return None


def socket_path(config: Optional[Config] = None) -> Path:
    """Return the Unix socket path for the whatwasit daemon."""
    runtime = _xdg_runtime_dir()
    if runtime is not None:
        primary = runtime / SOCKET_FILENAME
        legacy = runtime / LEGACY_SOCKET_FILENAME
        if primary.exists():
            return primary
        if legacy.exists():
            return legacy
        return primary
    data_dir = (config or Config.default()).data_dir
    primary = data_dir / SOCKET_FILENAME
    legacy = data_dir / LEGACY_SOCKET_FILENAME
    if primary.exists():
        return primary
    if legacy.exists():
        return legacy
    return primary


def pid_path(config: Optional[Config] = None) -> Path:
    return (config or Config.default()).data_dir / PID_FILENAME


def _search_result_to_dict(result: SearchResult) -> Dict[str, Any]:
    session = result.session
    return {
        "score": result.score,
        "matched_indices": result.matched_indices,
        "session": {
            "id": session.id,
            "start_ts": session.start_ts,
            "end_ts": session.end_ts,
            "cwd": session.cwd,
            "commands": [
                {
                    "raw_cmd": c.raw_cmd,
                    "ts": c.ts,
                    "source": c.source,
                    "cwd": c.cwd,
                    "duration": c.duration,
                    "exit_code": c.exit_code,
                }
                for c in session.commands
            ],
        },
    }


def _search_result_from_dict(data: Dict[str, Any]) -> SearchResult:
    sdata = data["session"]
    commands = [Command(**c) for c in sdata.get("commands", [])]
    session = Session(
        id=sdata.get("id"),
        start_ts=sdata.get("start_ts"),
        end_ts=sdata.get("end_ts"),
        cwd=sdata.get("cwd"),
        commands=commands,
    )
    return SearchResult(
        session=session,
        score=float(data["score"]),
        matched_indices=list(data.get("matched_indices", [])),
    )


class DaemonState:
    """Warm embedder + index, reloaded when on-disk assets change."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.embedder = build_embedder(config)
        self.embedder.encode(["warmup"])
        self.index = build_index(config)
        self._index_mtime: Optional[float] = None
        self._db_mtime: Optional[float] = None
        self._reload_index_if_needed()

    def _reload_index_if_needed(self) -> None:
        index_mtime = (
            self.config.index_path.stat().st_mtime
            if self.config.index_path.is_file()
            else None
        )
        db_mtime = (
            self.config.db_path.stat().st_mtime
            if self.config.db_path.is_file()
            else None
        )
        if index_mtime != self._index_mtime or db_mtime != self._db_mtime:
            self.index.load()
            self._index_mtime = index_mtime
            self._db_mtime = db_mtime

    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}

        if method == "ping":
            return {"id": req_id, "ok": True, "result": {"status": "ok"}}

        if method == "search":
            query = params.get("query", "")
            k = params.get("k")
            self._reload_index_if_needed()
            results = search(
                self.config,
                query,
                k=k,
                embedder=self.embedder,
                index=self.index,
            )
            return {
                "id": req_id,
                "ok": True,
                "result": {
                    "results": [_search_result_to_dict(r) for r in results],
                },
            }

        return {"id": req_id, "ok": False, "error": f"unknown method: {method!r}"}


def _handle_client(conn: socket.socket, state: DaemonState) -> None:
    conn.settimeout(_REQUEST_TIMEOUT)
    with conn.makefile("r", encoding="utf-8") as reader:
        for line in reader:
            if len(line) > _MAX_REQUEST_BYTES:
                response = {"ok": False, "error": "request too large"}
                conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
                return
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = state.handle(request)
            except json.JSONDecodeError as exc:
                response = {"ok": False, "error": f"invalid json: {exc}"}
            except Exception as exc:  # noqa: BLE001 - return error to client
                response = {"ok": False, "error": str(exc)}
            conn.sendall((json.dumps(response) + "\n").encode("utf-8"))


def serve(config: Optional[Config] = None) -> int:
    """Run the daemon in the foreground (used after double-fork)."""
    config = config or Config.default()
    config.ensure_data_dir()
    sock_path = socket_path(config)
    sock_path.parent.mkdir(parents=True, exist_ok=True)
    if sock_path.exists():
        sock_path.unlink()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(sock_path))
    try:
        os.chmod(sock_path, 0o600)
    except OSError:
        pass
    server.listen(8)
    state = DaemonState(config)

    def _shutdown(signum, frame) -> None:  # noqa: ARG001
        server.close()
        if sock_path.exists():
            sock_path.unlink()
        pid_path(config).unlink(missing_ok=True)
        sys.exit(0)

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)

    while True:
        conn, _ = server.accept()
        with conn:
            _handle_client(conn, state)


def start_daemon(config: Optional[Config] = None) -> int:
    """Fork a background daemon process."""
    config = config or Config.default()
    config.ensure_data_dir()
    pid_file = pid_path(config)
    if pid_file.is_file():
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            print(f"{CLI_NAME} daemon already running (pid {pid})")
            return 0
        except (OSError, ValueError):
            pid_file.unlink(missing_ok=True)

    if os.fork() > 0:
        return 0

    os.setsid()
    if os.fork() > 0:
        sys.exit(0)

    with open(os.devnull, "w") as devnull:
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())

    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    return serve(config)


def stop_daemon(config: Optional[Config] = None) -> int:
    config = config or Config.default()
    pid_file = pid_path(config)
    if not pid_file.is_file():
        print(f"{CLI_NAME} daemon is not running")
        return 1
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
    except (OSError, ValueError):
        pid_file.unlink(missing_ok=True)
        socket_path(config).unlink(missing_ok=True)
        print(f"{CLI_NAME} daemon is not running")
        return 1
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        print(f"{CLI_NAME} daemon stop failed: {exc}")
        pid_file.unlink(missing_ok=True)
        return 1

    for _ in range(20):
        time.sleep(0.1)
        try:
            os.kill(pid, 0)
        except OSError:
            pid_file.unlink(missing_ok=True)
            socket_path(config).unlink(missing_ok=True)
            print(f"{CLI_NAME} daemon stopped")
            return 0
    print(f"{CLI_NAME} daemon did not exit in time")
    return 1


def _wait_for_daemon(config: Config, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = _rpc(config, {"id": 0, "method": "ping", "params": {}})
        if response and response.get("ok"):
            return True
        time.sleep(0.2)
    return False


def daemon_status(config: Optional[Config] = None) -> int:
    config = config or Config.default()
    response = _rpc(config, {"id": 1, "method": "ping", "params": {}})
    if response and response.get("ok"):
        print(f"{CLI_NAME} daemon is running")
        return 0
    pid_file = pid_path(config)
    if pid_file.is_file():
        print(f"{CLI_NAME} daemon pid file present but socket unreachable")
        return 1
    print(f"{CLI_NAME} daemon is not running")
    return 1


def _rpc(config: Config, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(_CONNECT_TIMEOUT)
    try:
        sock.connect(str(socket_path(config)))
    except OSError:
        return None

    try:
        sock.settimeout(_REQUEST_TIMEOUT)
        sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
        chunks: List[bytes] = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break
        if not chunks:
            return None
        line = b"".join(chunks).split(b"\n", 1)[0]
        return json.loads(line.decode("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    finally:
        sock.close()


def daemon_search(
    config: Config,
    query: str,
    k: Optional[int] = None,
) -> Optional[List[SearchResult]]:
    """Issue a search RPC to the daemon, or return None if unavailable."""
    response = _rpc(
        config,
        {
            "id": 1,
            "method": "search",
            "params": {"query": query, "k": k},
        },
    )
    if not response or not response.get("ok"):
        return None
    result = response.get("result") or {}
    return [_search_result_from_dict(item) for item in result.get("results", [])]
