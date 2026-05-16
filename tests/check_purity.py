#!/usr/bin/env python3
from pathlib import Path

forbidden = {".c", ".cc", ".cpp", ".cxx", ".rs", ".go", ".zig", ".cs", ".java", ".js", ".ts"}
allowed_dirs = {"tests", "docs", ".github"}
violations = []
for path in Path(".").rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    if path.parts[0] in allowed_dirs:
        continue
    if path.suffix in forbidden:
        violations.append(str(path))
if violations:
    raise SystemExit("non-assembly implementation files found:\n" + "\n".join(violations))
print("purity check passed")
