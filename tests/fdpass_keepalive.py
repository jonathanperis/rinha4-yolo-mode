#!/usr/bin/env python3
import array
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: fdpass_keepalive.py <api-binary>")

binary = sys.argv[1]
REQUEST = (
    b"POST /fraud-score HTTP/1.1\r\nHost: localhost\r\n"
    b"Content-Type: application/json\r\nContent-Length: 13\r\n\r\n"
    b'{"id":"tx-1"}'
)


def send_fd(ctrl: socket.socket, client_fd: int) -> None:
    fds = array.array("i", [client_fd])
    ctrl.sendmsg([b"x"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])


def wait_for_control_socket(sock_path: str, timeout: float = 3.0) -> socket.socket:
    deadline = time.time() + timeout
    ctrl = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    while True:
        try:
            ctrl.connect(sock_path)
            return ctrl
        except OSError:
            if time.time() > deadline:
                ctrl.close()
                raise
            time.sleep(0.02)


def assert_responses_on_one_passed_fd(ctrl: socket.socket, requests: list[tuple[bytes, bytes]]) -> None:
    """Send one inherited client fd and verify all requests on that connection."""
    client, server = socket.socketpair()
    client.settimeout(1)
    try:
        send_fd(ctrl, server.fileno())
        server.close()
        server = None
        for request, expected in requests:
            client.sendall(request)
            response = client.recv(512)
            assert b"200 OK" in response and expected in response, response
    finally:
        client.close()
        if server is not None:
            server.close()


with tempfile.TemporaryDirectory(prefix="rinha-api-") as tmpdir:
    sock_path = str(Path(tmpdir) / "api.sock")
    proc = subprocess.Popen([binary, sock_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ctrl = wait_for_control_socket(sock_path)
        try:
            ready = b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n"
            assert_responses_on_one_passed_fd(ctrl, [(ready, b"OK"), (REQUEST, b"fraud_score")])
            assert_responses_on_one_passed_fd(ctrl, [(REQUEST, b"fraud_score")])
        finally:
            ctrl.close()
        print("fdpass keepalive smoke passed")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)
