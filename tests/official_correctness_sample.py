#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import time

if len(sys.argv) != 2:
    raise SystemExit("usage: official_correctness_sample.py <api-binary>")

binary = sys.argv[1]
# Sampled from official rinha-de-backend-2026 test/test-data.json at 64acf78
# (preview dataset stats: 54100 total, 24058 fraud, 30042 legit, 797 edge cases).
CASES = [({'id': 'tx-1329056812', 'transaction': {'amount': 2508.13, 'installments': 7, 'requested_at': '2026-03-11T03:45:53Z'}, 'customer': {'avg_amount': 209.74, 'tx_count_24h': 13, 'known_merchants': ['MERC-003', 'MERC-016']}, 'merchant': {'id': 'MERC-089', 'mcc': '7801', 'avg_amount': 25.15}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 667.7296579973}, 'last_transaction': None}, False), ({'id': 'tx-3576980410', 'transaction': {'amount': 384.88, 'installments': 3, 'requested_at': '2026-03-11T20:23:35Z'}, 'customer': {'avg_amount': 769.76, 'tx_count_24h': 3, 'known_merchants': ['MERC-009', 'MERC-009', 'MERC-001', 'MERC-001']}, 'merchant': {'id': 'MERC-001', 'mcc': '5912', 'avg_amount': 298.95}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 13.7090520965}, 'last_transaction': {'timestamp': '2026-03-11T14:58:35Z', 'km_from_current': 18.8626479774}}, True), ({'id': 'tx-1788243118', 'transaction': {'amount': 4368.82, 'installments': 8, 'requested_at': '2026-03-17T02:04:06Z'}, 'customer': {'avg_amount': 68.88, 'tx_count_24h': 18, 'known_merchants': ['MERC-004', 'MERC-004', 'MERC-015', 'MERC-017', 'MERC-007']}, 'merchant': {'id': 'MERC-062', 'mcc': '7801', 'avg_amount': 25.55}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 881.6139684714}, 'last_transaction': {'timestamp': '2026-03-17T01:58:06Z', 'km_from_current': 660.9200962961}}, False), ({'id': 'tx-2549846621', 'transaction': {'amount': 2438.21, 'installments': 4, 'requested_at': '2026-03-12T07:45:51Z'}, 'customer': {'avg_amount': 278.8, 'tx_count_24h': 11, 'known_merchants': ['MERC-012', 'MERC-015', 'MERC-010', 'MERC-018']}, 'merchant': {'id': 'MERC-039', 'mcc': '5311', 'avg_amount': 185.09}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 206.517733351}, 'last_transaction': None}, True), ({'id': 'tx-176047310', 'transaction': {'amount': 691.01, 'installments': 4, 'requested_at': '2026-03-13T10:18:45Z'}, 'customer': {'avg_amount': 186.21, 'tx_count_24h': 6, 'known_merchants': ['MERC-007', 'MERC-005', 'MERC-017']}, 'merchant': {'id': 'MERC-007', 'mcc': '5812', 'avg_amount': 225.56}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 203.3907554609}, 'last_transaction': {'timestamp': '2026-03-13T09:38:45Z', 'km_from_current': 186.8106282611}}, False), ({'id': 'tx-1288306307', 'transaction': {'amount': 878.11, 'installments': 4, 'requested_at': '2026-03-26T09:57:57Z'}, 'customer': {'avg_amount': 334.71, 'tx_count_24h': 5, 'known_merchants': ['MERC-010', 'MERC-016', 'MERC-004']}, 'merchant': {'id': 'MERC-032', 'mcc': '4511', 'avg_amount': 238.8}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 84.2436349518}, 'last_transaction': {'timestamp': '2026-03-26T09:35:57Z', 'km_from_current': 186.8122980387}}, False), ({'id': 'tx-503233111', 'transaction': {'amount': 2159.76, 'installments': 3, 'requested_at': '2026-03-18T21:55:41Z'}, 'customer': {'avg_amount': 183.7, 'tx_count_24h': 11, 'known_merchants': ['MERC-004', 'MERC-005', 'MERC-014', 'MERC-013']}, 'merchant': {'id': 'MERC-004', 'mcc': '4511', 'avg_amount': 138.66}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 77.897534945}, 'last_transaction': {'timestamp': '2026-03-18T21:17:41Z', 'km_from_current': 141.8991641518}}, True), ({'id': 'tx-2463463058', 'transaction': {'amount': 567.81, 'installments': 4, 'requested_at': '2026-03-23T16:25:31Z'}, 'customer': {'avg_amount': 146.45, 'tx_count_24h': 7, 'known_merchants': ['MERC-010', 'MERC-011']}, 'merchant': {'id': 'MERC-043', 'mcc': '7801', 'avg_amount': 278.43}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 181.2813469421}, 'last_transaction': {'timestamp': '2026-03-23T14:52:31Z', 'km_from_current': 251.5968455448}}, True), ({'id': 'tx-1552880071', 'transaction': {'amount': 603.17, 'installments': 3, 'requested_at': '2026-03-24T20:42:30Z'}, 'customer': {'avg_amount': 363.36, 'tx_count_24h': 8, 'known_merchants': ['MERC-011', 'MERC-015', 'MERC-002']}, 'merchant': {'id': 'MERC-002', 'mcc': '5812', 'avg_amount': 165.45}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 290.2241864545}, 'last_transaction': {'timestamp': '2026-03-24T19:59:30Z', 'km_from_current': 35.9420544505}}, False), ({'id': 'tx-2349355895', 'transaction': {'amount': 2620.36, 'installments': 6, 'requested_at': '2026-03-18T06:34:57Z'}, 'customer': {'avg_amount': 381.54, 'tx_count_24h': 7, 'known_merchants': ['MERC-008', 'MERC-017', 'MERC-001', 'MERC-019', 'MERC-015']}, 'merchant': {'id': 'MERC-017', 'mcc': '5944', 'avg_amount': 212.61}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 206.9594857881}, 'last_transaction': {'timestamp': '2026-03-18T05:27:57Z', 'km_from_current': 101.034154082}}, False), ({'id': 'tx-3359272267', 'transaction': {'amount': 191.58, 'installments': 3, 'requested_at': '2026-03-26T20:32:01Z'}, 'customer': {'avg_amount': 383.16, 'tx_count_24h': 1, 'known_merchants': ['MERC-002', 'MERC-014', 'MERC-003', 'MERC-005', 'MERC-011']}, 'merchant': {'id': 'MERC-002', 'mcc': '5912', 'avg_amount': 62.82}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 10.9100236816}, 'last_transaction': {'timestamp': '2026-03-26T17:49:01Z', 'km_from_current': 5.377045927}}, True), ({'id': 'tx-858810831', 'transaction': {'amount': 449.61, 'installments': 3, 'requested_at': '2026-03-26T14:01:11Z'}, 'customer': {'avg_amount': 899.22, 'tx_count_24h': 2, 'known_merchants': ['MERC-005', 'MERC-014', 'MERC-018', 'MERC-010']}, 'merchant': {'id': 'MERC-010', 'mcc': '5812', 'avg_amount': 242.61}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 45.9354921933}, 'last_transaction': {'timestamp': '2026-03-26T04:31:11Z', 'km_from_current': 15.7078867163}}, True), ({'id': 'tx-4086599650', 'transaction': {'amount': 5170.97, 'installments': 9, 'requested_at': '2026-03-18T06:11:39Z'}, 'customer': {'avg_amount': 177.29, 'tx_count_24h': 14, 'known_merchants': ['MERC-013', 'MERC-008', 'MERC-006']}, 'merchant': {'id': 'MERC-076', 'mcc': '7801', 'avg_amount': 81.07}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 715.1167677052}, 'last_transaction': {'timestamp': '2026-03-18T06:03:39Z', 'km_from_current': 346.5745611458}}, False), ({'id': 'tx-3975988070', 'transaction': {'amount': 6235.49, 'installments': 6, 'requested_at': '2026-03-10T04:44:08Z'}, 'customer': {'avg_amount': 141.14, 'tx_count_24h': 17, 'known_merchants': ['MERC-018', 'MERC-011', 'MERC-003']}, 'merchant': {'id': 'MERC-073', 'mcc': '7802', 'avg_amount': 39.78}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 289.2708549484}, 'last_transaction': None}, False), ({'id': 'tx-96985532', 'transaction': {'amount': 5589.38, 'installments': 10, 'requested_at': '2026-03-14T03:47:03Z'}, 'customer': {'avg_amount': 99.6, 'tx_count_24h': 16, 'known_merchants': ['MERC-017', 'MERC-001']}, 'merchant': {'id': 'MERC-063', 'mcc': '7802', 'avg_amount': 64.56}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 497.5950506277}, 'last_transaction': {'timestamp': '2026-03-14T03:40:03Z', 'km_from_current': 665.7882278007}}, False), ({'id': 'tx-330608576', 'transaction': {'amount': 106.05, 'installments': 1, 'requested_at': '2026-03-12T15:50:56Z'}, 'customer': {'avg_amount': 212.1, 'tx_count_24h': 1, 'known_merchants': ['MERC-010', 'MERC-005']}, 'merchant': {'id': 'MERC-005', 'mcc': '5812', 'avg_amount': 201.35}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 3.0300579157}, 'last_transaction': None}, True), ({'id': 'tx-3830345816', 'transaction': {'amount': 90.2, 'installments': 3, 'requested_at': '2026-03-15T19:22:02Z'}, 'customer': {'avg_amount': 180.4, 'tx_count_24h': 4, 'known_merchants': ['MERC-011', 'MERC-003']}, 'merchant': {'id': 'MERC-011', 'mcc': '5912', 'avg_amount': 46.76}, 'terminal': {'is_online': False, 'card_present': True, 'km_from_home': 15.8569043306}, 'last_transaction': {'timestamp': '2026-03-15T14:41:02Z', 'km_from_current': 4.6107363572}}, True), ({'id': 'tx-856410551', 'transaction': {'amount': 2146.61, 'installments': 7, 'requested_at': '2026-03-27T11:04:03Z'}, 'customer': {'avg_amount': 407.95, 'tx_count_24h': 7, 'known_merchants': ['MERC-018', 'MERC-003', 'MERC-018']}, 'merchant': {'id': 'MERC-018', 'mcc': '5999', 'avg_amount': 218.56}, 'terminal': {'is_online': True, 'card_present': False, 'km_from_home': 348.5748756813}, 'last_transaction': {'timestamp': '2026-03-27T10:58:03Z', 'km_from_current': 30.5517783227}}, False)]


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
