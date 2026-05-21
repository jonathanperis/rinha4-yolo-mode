#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import time

if len(sys.argv) != 2:
    raise SystemExit("usage: official_correctness_sample.py <api-binary>")

binary = sys.argv[1]
CASES = [({'id': 'tx-2611557002', 'transaction': {'amount': 2420.26, 'installments': 7, 'requested_at': '2027-04-06T20:54:28Z'}, 'customer': {'avg_amount': 194.3, 'tx_count_24h': 9, 'known_merchants': ['MERC-007', 'MERC-009', 'MERC-009']}, 'merchant': {'id': 'MERC-007', 'mcc': '7802', 'avg_amount': 183.81}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 229.0227050332}, 'last_transaction': {'timestamp': '2025-02-08T05:19:41Z', 'km_from_current': 90.9077316595}}, True), ({'id': 'tx-869781288', 'transaction': {'amount': 4688.21, 'installments': 7, 'requested_at': '2030-01-16T05:40:46Z'}, 'customer': {'avg_amount': 279.1, 'tx_count_24h': 10, 'known_merchants': ['MERC-016', 'MERC-019']}, 'merchant': {'id': 'MERC-065', 'mcc': '7801', 'avg_amount': 49.58}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 374.2347002435}, 'last_transaction': {'timestamp': '2024-01-10T20:33:34Z', 'km_from_current': 232.2932645754}}, True), ({'id': 'tx-3032967406', 'transaction': {'amount': 1690.73, 'installments': 5, 'requested_at': '2028-03-22T17:18:49Z'}, 'customer': {'avg_amount': 407.19, 'tx_count_24h': 9, 'known_merchants': ['MERC-008', 'MERC-019', 'MERC-005']}, 'merchant': {'id': 'MERC-019', 'mcc': '5999', 'avg_amount': 52.31}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 345.454222815}, 'last_transaction': {'timestamp': '2023-08-09T21:58:56Z', 'km_from_current': 22.8355605348}}, True), ({'id': 'tx-3769056616', 'transaction': {'amount': 2667.9, 'installments': 3, 'requested_at': '2028-03-14T15:46:39Z'}, 'customer': {'avg_amount': 204.69, 'tx_count_24h': 7, 'known_merchants': ['MERC-002', 'MERC-008']}, 'merchant': {'id': 'MERC-054', 'mcc': '5311', 'avg_amount': 260.56}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 303.4333834363}, 'last_transaction': {'timestamp': '2021-10-15T12:02:26Z', 'km_from_current': 216.2886056295}}, False), ({'id': 'tx-230576467', 'transaction': {'amount': 2461.29, 'installments': 4, 'requested_at': '2027-09-26T08:07:52Z'}, 'customer': {'avg_amount': 365.52, 'tx_count_24h': 10, 'known_merchants': ['MERC-018', 'MERC-015', 'MERC-001', 'MERC-010']}, 'merchant': {'id': 'MERC-010', 'mcc': '5912', 'avg_amount': 84.64}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 316.3911158211}, 'last_transaction': {'timestamp': '2022-03-29T14:05:43Z', 'km_from_current': 161.4518522894}}, True), ({'id': 'tx-3662423109', 'transaction': {'amount': 1317.26, 'installments': 6, 'requested_at': '2027-12-02T08:08:39Z'}, 'customer': {'avg_amount': 225.32, 'tx_count_24h': 7, 'known_merchants': ['MERC-015', 'MERC-011']}, 'merchant': {'id': 'MERC-053', 'mcc': '5311', 'avg_amount': 135.16}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 386.4076797889}, 'last_transaction': {'timestamp': '2021-02-13T19:07:03Z', 'km_from_current': 40.2307120292}}, True), ({'id': 'tx-1313898586', 'transaction': {'amount': 1335.69, 'installments': 3, 'requested_at': '2026-04-05T21:53:01Z'}, 'customer': {'avg_amount': 220.46, 'tx_count_24h': 6, 'known_merchants': ['MERC-014', 'MERC-017']}, 'merchant': {'id': 'MERC-057', 'mcc': '5311', 'avg_amount': 196.09}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 183.5505252037}, 'last_transaction': {'timestamp': '2018-11-26T20:47:23Z', 'km_from_current': 202.4587604642}}, False), ({'id': 'tx-1135548804', 'transaction': {'amount': 2394.23, 'installments': 6, 'requested_at': '2028-07-20T21:10:35Z'}, 'customer': {'avg_amount': 265.89, 'tx_count_24h': 7, 'known_merchants': ['MERC-011', 'MERC-008', 'MERC-014']}, 'merchant': {'id': 'MERC-014', 'mcc': '7802', 'avg_amount': 163.84}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 397.223265657}, 'last_transaction': {'timestamp': '2024-06-30T16:35:01Z', 'km_from_current': 230.6214137028}}, False), ({'id': 'tx-2275905966', 'transaction': {'amount': 444.1, 'installments': 6, 'requested_at': '2028-09-06T12:35:56Z'}, 'customer': {'avg_amount': 209.08, 'tx_count_24h': 5, 'known_merchants': ['MERC-017', 'MERC-001']}, 'merchant': {'id': 'MERC-048', 'mcc': '5411', 'avg_amount': 89.36}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 138.5030887086}, 'last_transaction': {'timestamp': '2023-06-28T04:51:45Z', 'km_from_current': 194.3837147612}}, False), ({'id': 'tx-3096600589', 'transaction': {'amount': 2774.1, 'installments': 3, 'requested_at': '2029-04-02T10:40:51Z'}, 'customer': {'avg_amount': 215.69, 'tx_count_24h': 7, 'known_merchants': ['MERC-017', 'MERC-004']}, 'merchant': {'id': 'MERC-036', 'mcc': '5999', 'avg_amount': 96.33}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 308.477532691}, 'last_transaction': {'timestamp': '2025-11-09T09:22:24Z', 'km_from_current': 145.516623828}}, True)]


def wait_ready(timeout=5.0):
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


def post(payload):
    body = json.dumps(payload, separators=(",", ":")).encode()
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
    return json.loads(data.split(b"\r\n\r\n", 1)[1])


proc = subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    wait_ready()
    failures = []
    for payload, expected_approved in CASES:
        got = post(payload)
        if got.get("approved") is not expected_approved:
            failures.append((payload["id"], expected_approved, got))
    if failures:
        raise AssertionError(f"official sample mismatches: {failures}")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)

print("official correctness sample passed")
