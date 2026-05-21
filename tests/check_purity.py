#!/usr/bin/env python3
from pathlib import Path

# Runtime implementation files must stay assembly-only. Test, docs, and CI code
# are exempt because they are not shipped as the participant runtime.
FORBIDDEN_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cxx",
    ".rs", ".go", ".zig", ".cs", ".java",
    ".js", ".ts",
}
ALLOWED_DIRS = {"tests", "docs", ".github", "build"}

FORBIDDEN_RUNTIME_PATHS = {
    "src/api/corpus_table.inc",
}
FORBIDDEN_RUNTIME_MARKERS = {
    "rinha-de-backend-2026/test/test-data.json",
    "public-corpus IDs",
    "corpus_score_bucket",
}

violations = []
for path in Path(".").rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    path_str = str(path)
    if path_str in FORBIDDEN_RUNTIME_PATHS:
        violations.append(f"forbidden runtime lookup artifact: {path_str}")
        continue
    if path.parts[0] in ALLOWED_DIRS:
        continue
    if path.suffix in FORBIDDEN_SUFFIXES:
        violations.append(str(path))
        continue
    if path.suffix in {".S", ".s", ".inc", "", ".mk"} or path.name in {"Makefile", "Dockerfile"}:
        try:
            text = path.read_text(errors="ignore")
        except UnicodeDecodeError:
            text = ""
        for marker in FORBIDDEN_RUNTIME_MARKERS:
            if marker in text:
                violations.append(f"forbidden test-payload lookup marker in {path_str}: {marker}")

if violations:
    raise SystemExit("non-assembly implementation files found:\n" + "\n".join(violations))

print("purity check passed")
