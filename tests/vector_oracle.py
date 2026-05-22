#!/usr/bin/env python3
"""Reference-vector oracle smoke test for /fraud-score.

This harness intentionally uses only the public, legal reference dataset and
normalization assets. It does not embed public test-payload IDs or labels.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import heapq
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
from typing import Any

DEFAULT_ROOT_CANDIDATES = [
    Path(os.environ["RINHA_OFFICIAL_ROOT"]) if "RINHA_OFFICIAL_ROOT" in os.environ else None,
    Path("/opt/data/github/zanfranceschi/rinha-de-backend-2026"),
    Path("/opt/data/github/official-rinha-de-backend-2026"),
    Path("/opt/data/github/jonathanperis/official-rinha-de-backend-2026"),
]

SYNTHETIC_CASES: list[dict[str, Any]] = [
    {
        "id": "oracle-doc-legit",
        "transaction": {"amount": 41.12, "installments": 2, "requested_at": "2026-03-11T18:45:53Z"},
        "customer": {"avg_amount": 82.24, "tx_count_24h": 3, "known_merchants": ["MERC-003", "MERC-016"]},
        "merchant": {"id": "MERC-016", "mcc": "5411", "avg_amount": 60.25},
        "terminal": {"is_online": False, "card_present": True, "km_from_home": 29.23},
        "last_transaction": None,
    },
    {
        "id": "oracle-doc-fraud",
        "transaction": {"amount": 9505.97, "installments": 10, "requested_at": "2026-03-14T05:15:12Z"},
        "customer": {"avg_amount": 81.28, "tx_count_24h": 20, "known_merchants": ["MERC-008", "MERC-007", "MERC-005"]},
        "merchant": {"id": "MERC-068", "mcc": "7802", "avg_amount": 54.86},
        "terminal": {"is_online": False, "card_present": True, "km_from_home": 952.27},
        "last_transaction": None,
    },
    # This is a legal synthetic payload, not a public evaluator fixture. The
    # current heuristic path over-scores it; vector search over the reference set
    # finds all-legit neighbors in the default sampled oracle.
    {
        "id": "oracle-known-merchant-mid-amount",
        "transaction": {"amount": 500.0, "installments": 1, "requested_at": "2026-03-11T18:45:53Z"},
        "customer": {"avg_amount": 100.0, "tx_count_24h": 0, "known_merchants": ["MERC-001"]},
        "merchant": {"id": "MERC-001", "mcc": "5411", "avg_amount": 100.0},
        "terminal": {"is_online": False, "card_present": True, "km_from_home": 10.0},
        "last_transaction": None,
    },
]


def clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def norm4(value: float) -> float:
    return round(value, 4)


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_resources_root(explicit: str | None) -> Path:
    candidates = [Path(explicit)] if explicit else [p for p in DEFAULT_ROOT_CANDIDATES if p is not None]
    for root in candidates:
        if (root / "resources" / "references.json.gz").exists():
            return root
    searched = ", ".join(str(p) for p in candidates)
    raise SystemExit(f"could not find resources/references.json.gz; searched: {searched}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def vectorize(payload: dict[str, Any], normalization: dict[str, float], mcc_risk: dict[str, float]) -> list[float]:
    tx = payload["transaction"]
    customer = payload["customer"]
    merchant = payload["merchant"]
    terminal = payload["terminal"]
    requested_at = parse_utc(tx["requested_at"])
    last = payload.get("last_transaction")

    amount = float(tx["amount"])
    customer_avg = float(customer.get("avg_amount") or 0.0)
    amount_vs_avg = 1.0 if customer_avg <= 0.0 else (amount / customer_avg) / float(normalization["amount_vs_avg_ratio"])

    if last is None:
        minutes_since_last = -1.0
        km_from_last = -1.0
    else:
        last_at = parse_utc(last["timestamp"])
        minutes_since_last = clamp((requested_at - last_at).total_seconds() / 60.0 / float(normalization["max_minutes"]))
        km_from_last = clamp(float(last["km_from_current"]) / float(normalization["max_km"]))

    return [
        norm4(clamp(amount / float(normalization["max_amount"]))),
        norm4(clamp(float(tx["installments"]) / float(normalization["max_installments"]))),
        norm4(clamp(amount_vs_avg)),
        norm4(requested_at.hour / 23.0),
        norm4(requested_at.weekday() / 6.0),
        -1.0 if minutes_since_last < 0.0 else norm4(minutes_since_last),
        -1.0 if km_from_last < 0.0 else norm4(km_from_last),
        norm4(clamp(float(terminal["km_from_home"]) / float(normalization["max_km"]))),
        norm4(clamp(float(customer["tx_count_24h"]) / float(normalization["max_tx_count_24h"]))),
        1.0 if terminal["is_online"] else 0.0,
        1.0 if terminal["card_present"] else 0.0,
        0.0 if merchant["id"] in customer.get("known_merchants", []) else 1.0,
        float(mcc_risk.get(str(merchant["mcc"]), 0.5)),
        norm4(clamp(float(merchant["avg_amount"]) / float(normalization["max_merchant_avg_amount"]))),
    ]


def load_references(path: Path, limit: int) -> list[tuple[list[float], bool]]:
    refs: list[tuple[list[float], bool]] = []
    with gzip.open(path, "rt") as f:
        for item in json.load(f):
            refs.append((item["vector"], item["label"] == "fraud"))
            if limit and len(refs) >= limit:
                break
    if len(refs) < 5:
        raise SystemExit(f"reference sample too small: {len(refs)}")
    return refs


def oracle_bucket(vector: list[float], refs: list[tuple[list[float], bool]]) -> int:
    best: list[tuple[float, int, bool]] = []
    for idx, (ref_vector, is_fraud) in enumerate(refs):
        dist = sum((a - b) * (a - b) for a, b in zip(vector, ref_vector))
        item = (-dist, -idx, is_fraud)
        if len(best) < 5:
            heapq.heappush(best, item)
        elif item > best[0]:
            heapq.heapreplace(best, item)
    return sum(1 for _, _, is_fraud in best if is_fraud)


def wait_ready(timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 9999), timeout=0.2) as sock:
                sock.sendall(b"GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n")
                data = sock.recv(1024)
                if b"HTTP/1.1 200 OK" in data and b"OK" in data:
                    return
        except OSError as exc:
            last_error = exc
            time.sleep(0.02)
    raise RuntimeError(f"server did not become ready: {last_error}")


def post_fraud_score(payload: dict[str, Any]) -> float:
    body = json.dumps(payload, separators=(",", ":")).encode()
    req = (
        b"POST /fraud-score HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
    )
    with socket.create_connection(("127.0.0.1", 9999), timeout=1) as sock:
        sock.sendall(req)
        data = sock.recv(4096)
    if b"HTTP/1.1 200 OK" not in data:
        raise AssertionError(data.decode(errors="replace"))
    match = re.search(rb'"fraud_score":([0-9.]+)', data)
    if not match:
        raise AssertionError(data.decode(errors="replace"))
    return float(match.group(1))


def run(args: argparse.Namespace) -> int:
    root = find_resources_root(args.resources_root)
    normalization = load_json(root / "resources" / "normalization.json")
    mcc_risk = load_json(root / "resources" / "mcc_risk.json")
    refs = load_references(root / "resources" / "references.json.gz", args.ref_limit)

    proc = subprocess.Popen([args.binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_ready()
        mismatches = []
        for payload in SYNTHETIC_CASES:
            vector = vectorize(payload, normalization, mcc_risk)
            expected_bucket = oracle_bucket(vector, refs)
            expected_score = expected_bucket / 5.0
            actual_score = post_fraud_score(payload)
            if abs(actual_score - expected_score) > 1e-9:
                mismatches.append((payload["id"], expected_score, actual_score, vector))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)

    if mismatches:
        lines = [
            f"oracle mismatches using {len(refs)} legal references from {root}:",
            *(
                f"  {case_id}: oracle={expected:.1f} api={actual:.1f} vector={vector}"
                for case_id, expected, actual, vector in mismatches
            ),
        ]
        raise SystemExit("\n".join(lines))

    print(f"vector oracle smoke passed ({len(refs)} legal references)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", help="path to API binary")
    parser.add_argument("--resources-root", help="official rinha-de-backend-2026 checkout root")
    parser.add_argument("--ref-limit", type=int, default=int(os.environ.get("ORACLE_REF_LIMIT", "50000")))
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
