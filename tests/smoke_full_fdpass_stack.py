#!/usr/bin/env python3
import socket
import subprocess
import sys
import time
from pathlib import Path

api_bin = sys.argv[1]
lb_bin = sys.argv[2]
run_dir = Path("/tmp/rinha")
run_dir.mkdir(parents=True, exist_ok=True)
paths = [run_dir / "api1.sock", run_dir / "api2.sock"]
for path in paths:
    try:
        path.unlink()
    except FileNotFoundError:
        pass

procs = []
try:
    for path in paths:
        procs.append(subprocess.Popen([api_bin, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE))

    deadline = time.time() + 5
    while time.time() < deadline and not all(path.exists() for path in paths):
        time.sleep(0.02)
    assert all(path.exists() for path in paths), paths

    lb = subprocess.Popen([lb_bin], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    procs.append(lb)

    deadline = time.time() + 5
    last_error = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=0.2) as s:
                s.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
                data = s.recv(1024)
                assert data.endswith(b"OK"), data
                break
        except Exception as exc:
            last_error = exc
            time.sleep(0.05)
    else:
        raise SystemExit(f"full stack /ready failed: {last_error}")

    def post(body: bytes) -> bytes:
        with socket.create_connection(("127.0.0.1", 9999), timeout=1) as s:
            req = b"POST /fraud-score HTTP/1.1\r\nHost: localhost\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
            s.sendall(req)
            return s.recv(2048)

    data = post(b'{"id":"tx-smoke","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.0}' in data, data

    data = post(b'{"id":"tx-medium","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":10},"terminal":{"is_online":false,"card_present":true}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"amount-installments","transaction":{"amount":10000,"installments":12},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.4}' in data, data

    data = post(b'{"id":"ratio-risk","transaction":{"amount":600,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-001","mcc":"5912","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"merchant-geo-risk","transaction":{"amount":100,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-999","mcc":"7995","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":700}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.6}' in data, data

    data = post(b'{"id":"time-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T02:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"last-transaction-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T20:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true},"last_transaction":{"timestamp":"2026-03-11T20:18:35Z","km_from_current":700}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.4}' in data, data

    data = post(b'{"id":"terminal-risk","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.8}' in data, data

    data = post(b'{"id":"full-risk","transaction":{"amount":10000,"installments":12},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":1.0}' in data, data
finally:
    for proc in reversed(procs):
        proc.terminate()
    for proc in reversed(procs):
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

print("asm full fdpass stack smoke passed")
