#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: corpus_replay.py <api-binary> <test-data.json>")

binary = sys.argv[1]
corpus_path = Path(sys.argv[2])
limit = int(os.environ.get("CORPUS_REPLAY_LIMIT", "0") or "0")

entries = json.loads(corpus_path.read_text())["entries"]
if limit > 0:
    entries = entries[:limit]

proc = subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    deadline = time.time() + 5
    last_error = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=0.2) as s:
                s.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
                data = s.recv(1024)
                if b"HTTP/1.1 200 OK" in data:
                    break
        except Exception as exc:
            last_error = exc
            time.sleep(0.02)
    else:
        raise SystemExit(f"/ready failed before corpus replay: {last_error}")

    false_positives = 0
    false_negatives = 0
    http_errors = 0
    score_mismatches = 0
    first_errors = []

    for i, entry in enumerate(entries, 1):
        body = json.dumps(entry["request"], separators=(",", ":")).encode()
        req = (
            b"POST /fraud-score HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
        )
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=1) as s:
                s.sendall(req)
                data = s.recv(2048)
        except Exception as exc:
            http_errors += 1
            if len(first_errors) < 10:
                first_errors.append((entry["request"].get("id"), "socket", repr(exc)))
            continue
        if b"HTTP/1.1 200 OK" not in data or b"\r\n\r\n" not in data:
            http_errors += 1
            if len(first_errors) < 10:
                first_errors.append((entry["request"].get("id"), "http", data[:200].decode("latin1", "replace")))
            continue
        payload = data.split(b"\r\n\r\n", 1)[1]
        try:
            response = json.loads(payload)
            approved = bool(response["approved"])
            score = float(response["fraud_score"])
        except Exception:
            http_errors += 1
            if len(first_errors) < 10:
                first_errors.append((entry["request"].get("id"), "json", payload.decode("latin1", "replace")))
            continue

        expected_approved = bool(entry["expected_approved"])
        expected_score = float(entry["expected_fraud_score"])
        if approved != expected_approved:
            if approved and not expected_approved:
                false_negatives += 1
            else:
                false_positives += 1
            if len(first_errors) < 10:
                first_errors.append((entry["request"].get("id"), "approval", response, expected_approved, expected_score))
        if abs(score - expected_score) > 1e-9:
            score_mismatches += 1
            if len(first_errors) < 10:
                first_errors.append((entry["request"].get("id"), "score", response, expected_approved, expected_score))

    print(f"total: {len(entries)}")
    print(f"false positives: {false_positives}")
    print(f"false negatives: {false_negatives}")
    print(f"http errors: {http_errors}")
    print(f"score mismatches: {score_mismatches}")
    if first_errors:
        print("first errors:")
        for error in first_errors:
            print(repr(error))
    if false_positives or false_negatives or http_errors or score_mismatches:
        raise SystemExit(1)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)
