#!/usr/bin/env python3
import socket
import subprocess
import sys
import time

binary = sys.argv[1]
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
                assert data.endswith(b"OK"), data
                break
        except Exception as exc:  # server may still be binding
            last_error = exc
            time.sleep(0.05)
    else:
        raise SystemExit(f"/ready smoke failed: {last_error}")

    with socket.create_connection(("127.0.0.1", 9999), timeout=1) as s:
        body = b'{"id":"tx-smoke"}'
        req = b"POST /fraud-score HTTP/1.1\r\nHost: localhost\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
        s.sendall(req)
        data = s.recv(2048)
        assert b"HTTP/1.1 200 OK" in data, data
        assert b'{"approved":true,"fraud_score":0.0}' in data, data
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)

print("asm api smoke passed")
