#!/usr/bin/env python3
"""Source-backed documentation drift checks for high-value public claims."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    readme = read("README.md")
    site = read("docs/src/data/site.ts")
    product = read("PRODUCT.md")
    design = read("DESIGN.md")
    compose = read("docker-compose.yml")
    api = read("src/api/main.S")
    benchmark_workflow = read(".github/workflows/benchmark.yml")
    build_workflow = read(".github/workflows/build.yml")
    benchmark_script = read("scripts/ci-official-benchmark.sh")
    makefile = read("Makefile")

    # Compose resource split must match public/docs claims.
    require('cpus: "0.06"' in compose and 'memory: "30M"' in compose, "compose LB resource split changed")
    require(compose.count('cpus: "0.47"') == 2 and compose.count('memory: "160M"') == 2, "compose API resource split changed")
    for doc_name, text in [("README.md", readme), ("docs/src/data/site.ts", site), ("PRODUCT.md", product)]:
        require("0.06 CPU / 30M" in text, f"{doc_name} missing LB resource split")
        require("0.47 CPU / 160M" in text, f"{doc_name} missing API resource split")
        require("1 CPU / 350 MB" in text, f"{doc_name} missing total resource envelope")

    # Backlog distinction: LB compose knob and direct API smoke constant are different on purpose.
    require('BACKLOG: "65535"' in compose, "compose LB BACKLOG changed")
    require(re.search(r"\.equ\s+BACKLOG,\s*4096", api) is not None, "assembly direct-mode BACKLOG changed")
    for doc_name, text in [("README.md", readme), ("docs/src/data/site.ts", site)]:
        require("BACKLOG=65535" in text and "BACKLOG=4096" in text, f"{doc_name} missing backlog distinction")

    # Optional vector oracle must stay visible if the target exists.
    require("oracle-smoke:" in makefile and "tests/vector_oracle.py" in makefile, "Makefile oracle-smoke target changed")
    for doc_name, text in [("README.md", readme), ("docs/src/data/site.ts", site), ("DESIGN.md", design)]:
        require("oracle-smoke" in text, f"{doc_name} missing oracle-smoke documentation")

    # Official-like benchmark defaults and artifacts must not drift back to an old pinned ref.
    require('default: main' in benchmark_workflow, "benchmark workflow official_ref default changed")
    require('OFFICIAL_REF="${OFFICIAL_REF:-main}"' in benchmark_script, "benchmark script OFFICIAL_REF default changed")
    require("64acf788baef3c1687bba93c04357cc8c7082b11 by default" not in readme, "README still documents stale pinned benchmark ref")
    for doc_name, text in [("README.md", readme), ("docs/src/data/site.ts", site)]:
        require("OFFICIAL_REF=main" in text or "official_ref/OFFICIAL_REF=main" in text, f"{doc_name} missing benchmark main default")
        require("repetition-summary.json" in text, f"{doc_name} missing benchmark repetition artifacts")

    # Build/release tag and docs-only path-filter facts must stay documented.
    for marker in ["type=raw,value=latest", "type=raw,value=ci-${{ github.sha }}", "type=sha", "paths-ignore:"]:
        require(marker in build_workflow, f"build workflow missing expected marker {marker}")
    for doc_name, text in [("README.md", readme), ("docs/src/data/site.ts", site)]:
        require("ci-<" in text and "sha-*" in text and "docs/**" in text, f"{doc_name} missing release tag/path-filter documentation")

    print("docs drift check passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"docs drift check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
