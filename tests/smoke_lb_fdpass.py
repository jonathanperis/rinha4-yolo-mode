#!/usr/bin/env python3
import array
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

binary = sys.argv[1]
run_dir = Path("/tmp/rinha")
run_dir.mkdir(parents=True, exist_ok=True)
paths = [run_dir / "api1.sock", run_dir / "api2.sock"]
for path in paths:
    try:
        path.unlink()
    except FileNotFoundError:
        pass

seen = []
stop = threading.Event()
servers = []
threads = []


def recv_fd(ctrl):
    msg, ancdata, _flags, _addr = ctrl.recvmsg(1, socket.CMSG_SPACE(array.array("i", [0]).itemsize))
    if not msg:
        return None
    for level, typ, data in ancdata:
        if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            fds = array.array("i")
            fds.frombytes(data[: fds.itemsize])
            return fds[0]
    raise AssertionError(f"no fd received: {ancdata!r}")


def backend(name, path):
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(str(path))
    srv.listen(16)
    srv.settimeout(0.2)
    servers.append(srv)
    conns = []
    try:
        while not stop.is_set():
            try:
                ctrl, _ = srv.accept()
                ctrl.settimeout(0.2)
                conns.append(ctrl)
            except socket.timeout:
                pass
            for ctrl in list(conns):
                try:
                    fd = recv_fd(ctrl)
                except socket.timeout:
                    continue
                except (ConnectionError, OSError):
                    conns.remove(ctrl)
                    ctrl.close()
                    continue
                if fd is None:
                    continue
                with socket.socket(fileno=fd) as client:
                    client.settimeout(1)
                    data = client.recv(4096)
                    assert b"GET /ready" in data, data
                    body = name.encode()
                    resp = b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body
                    client.sendall(resp)
                    seen.append(name)
    finally:
        for ctrl in conns:
            ctrl.close()
        srv.close()


for name, path in [("api1", paths[0]), ("api2", paths[1])]:
    t = threading.Thread(target=backend, args=(name, path), daemon=True)
    t.start()
    threads.append(t)

# Wait until sockets exist before starting LB; the assembly LB connects at startup.
deadline = time.time() + 5
while time.time() < deadline and not all(path.exists() for path in paths):
    time.sleep(0.01)
assert all(path.exists() for path in paths), paths

proc = subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
try:
    deadline = time.time() + 5
    last_error = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=0.2) as s:
                s.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
                data = s.recv(1024)
                assert b"HTTP/1.1 200 OK" in data, data
                break
        except Exception as exc:
            last_error = exc
            time.sleep(0.05)
    else:
        raise SystemExit(f"lb fdpass smoke failed to connect: {last_error}; stderr={proc.stderr.read().decode(errors='ignore')}")

    for _ in range(3):
        with socket.create_connection(("127.0.0.1", 9999), timeout=1) as s:
            s.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
            data = s.recv(1024)
            assert data.endswith((b"api1", b"api2")), data

    deadline = time.time() + 2
    while time.time() < deadline and len(seen) < 4:
        time.sleep(0.01)
    assert seen[:4] == ["api2", "api1", "api2", "api1"], seen
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)
    stop.set()
    for srv in servers:
        try:
            srv.close()
        except OSError:
            pass
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

print("asm lb fdpass smoke passed")
