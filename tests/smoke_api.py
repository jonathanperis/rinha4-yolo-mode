#!/usr/bin/env python3
import socket
import subprocess
import sys
import time

if len(sys.argv) != 2:
    raise SystemExit("usage: smoke_api.py <api-binary>")

binary = sys.argv[1]


def wait_ready(timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=0.2) as s:
                s.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
                data = s.recv(1024)
                if b"HTTP/1.1 200 OK" in data and b"OK" in data:
                    return
        except OSError as exc:
            last_error = exc
            time.sleep(0.02)
    raise RuntimeError(f"server did not become ready: {last_error}")


def assert_post(body: bytes, expected: bytes) -> None:
    req = (
        b"POST /fraud-score HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
    )
    with socket.create_connection(("127.0.0.1", 9999), timeout=1) as s:
        s.sendall(req)
        data = s.recv(2048)
    assert b"HTTP/1.1 200 OK" in data, data
    assert expected in data, data


# Synthetic table-driven cases pin the payload-derived heuristic buckets.
# Do not add public preview/test payload IDs or expected labels here.
CASES = [
    (
        b'{"id":"case-low","transaction":{"amount":10,"installments":1},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}',
        b'{"approved":true,"fraud_score":0.0}',
    ),
    (
        b'{"id":"case-medium","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":10},"terminal":{"is_online":false,"card_present":true}}',
        b'{"approved":true,"fraud_score":0.2}',
    ),
    (
        b'{"id":"amount-installments","transaction":{"amount":10000,"installments":12},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"ratio-risk","transaction":{"amount":600,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-001","mcc":"5912","avg_amount":600},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"merchant-avg-ratio-risk","transaction":{"amount":600,"installments":1},"customer":{"avg_amount":600,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-001","mcc":"5912","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"merchant-geo-risk","transaction":{"amount":100,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-999","mcc":"7995","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":700}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"time-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T02:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}',
        b'{"approved":true,"fraud_score":0.2}',
    ),
    (
        b'{"id":"last-transaction-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T20:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true},"last_transaction":{"timestamp":"2026-03-11T20:18:35Z","km_from_current":700}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"mcc-table-risk","transaction":{"amount":100,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-780"]},"merchant":{"id":"MERC-780","mcc":"7802","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}',
        b'{"approved":true,"fraud_score":0.2}',
    ),
    (
        b'{"id":"terminal-risk","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}',
        b'{"approved":true,"fraud_score":0.4}',
    ),
    (
        b'{"id":"full-risk","transaction":{"amount":10000,"installments":12},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}',
        b'{"approved":false,"fraud_score":1.0}',
    ),
    # Documentation examples from DETECTION_RULES.md: one near-home known
    # merchant legit request and one high-risk unknown merchant request.
    (
        b'{"id":"doc-legit","transaction":{"amount":41.12,"installments":2,"requested_at":"2026-03-11T18:45:53Z"},"customer":{"avg_amount":82.24,"tx_count_24h":3,"known_merchants":["MERC-003","MERC-016"]},"merchant":{"id":"MERC-016","mcc":"5411","avg_amount":60.25},"terminal":{"is_online":false,"card_present":true,"km_from_home":29.23},"last_transaction":null}',
        b'{"approved":true,"fraud_score":0.0}',
    ),
    (
        b'{"id":"doc-fraud","transaction":{"amount":9505.97,"installments":10,"requested_at":"2026-03-14T05:15:12Z"},"customer":{"avg_amount":81.28,"tx_count_24h":20,"known_merchants":["MERC-008","MERC-007","MERC-005"]},"merchant":{"id":"MERC-068","mcc":"7802","avg_amount":54.86},"terminal":{"is_online":false,"card_present":true,"km_from_home":952.27},"last_transaction":null}',
        b'{"approved":false,"fraud_score":1.0}',
    ),
]

proc = subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    wait_ready()
    for body, expected in CASES:
        assert_post(body, expected)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)

print("asm api smoke passed")
