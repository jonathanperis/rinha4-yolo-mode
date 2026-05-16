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

    data = post(b'{"id":"ratio-risk","transaction":{"amount":600,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-001","mcc":"5912","avg_amount":600},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"merchant-avg-ratio-risk","transaction":{"amount":600,"installments":1},"customer":{"avg_amount":600,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-001","mcc":"5912","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"merchant-geo-risk","transaction":{"amount":100,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-001"]},"merchant":{"id":"MERC-999","mcc":"7995","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":700}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.4}' in data, data

    data = post(b'{"id":"official-legit-count3","transaction":{"amount":485,"installments":1,"requested_at":"2026-03-27T13:11:06Z"},"customer":{"avg_amount":971,"tx_count_24h":2,"known_merchants":["MERC-004","MERC-016","MERC-014","MERC-019","MERC-010"]},"merchant":{"id":"MERC-014","mcc":"5812","avg_amount":67},"terminal":{"is_online":true,"card_present":false,"km_from_home":2},"last_transaction":{"timestamp":"2026-03-27T08:35:06Z","km_from_current":14}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.4}' in data, data

    data = post(b'{"id":"official-fraud-count4","transaction":{"amount":1167,"installments":6,"requested_at":"2026-03-27T06:43:05Z"},"customer":{"avg_amount":158,"tx_count_24h":6,"known_merchants":["MERC-018","MERC-015"]},"merchant":{"id":"MERC-015","mcc":"4511","avg_amount":179},"terminal":{"is_online":true,"card_present":false,"km_from_home":322},"last_transaction":{"timestamp":"2026-03-27T05:44:05Z","km_from_current":119}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.6}' in data, data

    data = post(b'{"id":"tx-2549846621","transaction":{"amount":2438.21,"installments":4,"requested_at":"2026-03-12T07:45:51Z"},"customer":{"avg_amount":278.8,"tx_count_24h":11,"known_merchants":["MERC-012","MERC-015","MERC-010","MERC-018"]},"merchant":{"id":"MERC-039","mcc":"5311","avg_amount":185.09},"terminal":{"is_online":true,"card_present":false,"km_from_home":206.517733351},"last_transaction":null}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.0}' in data, data

    data = post(b'{"id":"tx-176047310","transaction":{"amount":691.01,"installments":4,"requested_at":"2026-03-13T10:18:45Z"},"customer":{"avg_amount":186.21,"tx_count_24h":6,"known_merchants":["MERC-007","MERC-005","MERC-017"]},"merchant":{"id":"MERC-007","mcc":"5812","avg_amount":225.56},"terminal":{"is_online":true,"card_present":false,"km_from_home":203.3907554609},"last_transaction":{"timestamp":"2026-03-13T09:38:45Z","km_from_current":186.8106282611}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.6}' in data, data

    data = post(b'{"id":"tx-1552880071","transaction":{"amount":603.17,"installments":3,"requested_at":"2026-03-24T20:42:30Z"},"customer":{"avg_amount":363.36,"tx_count_24h":8,"known_merchants":["MERC-011","MERC-015","MERC-002"]},"merchant":{"id":"MERC-002","mcc":"5812","avg_amount":165.45},"terminal":{"is_online":false,"card_present":true,"km_from_home":290.2241864545},"last_transaction":{"timestamp":"2026-03-24T19:59:30Z","km_from_current":35.9420544505}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.8}' in data, data

    data = post(b'{"id":"time-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T02:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"last-transaction-risk","transaction":{"amount":100,"installments":1,"requested_at":"2026-03-11T20:23:35Z"},"customer":{"tx_count_24h":0},"terminal":{"is_online":false,"card_present":true},"last_transaction":{"timestamp":"2026-03-11T20:18:35Z","km_from_current":700}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.4}' in data, data

    data = post(b'{"id":"mcc-table-risk","transaction":{"amount":100,"installments":1},"customer":{"avg_amount":100,"tx_count_24h":0,"known_merchants":["MERC-780"]},"merchant":{"id":"MERC-780","mcc":"7802","avg_amount":100},"terminal":{"is_online":false,"card_present":true,"km_from_home":10}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":true,"fraud_score":0.2}' in data, data

    data = post(b'{"id":"terminal-risk","transaction":{"amount":100,"installments":1},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":0.6}' in data, data

    data = post(b'{"id":"full-risk","transaction":{"amount":10000,"installments":12},"customer":{"tx_count_24h":20},"terminal":{"is_online":true,"card_present":false}}')
    assert b"HTTP/1.1 200 OK" in data, data
    assert b'{"approved":false,"fraud_score":1.0}' in data, data
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)

print("asm api smoke passed")
