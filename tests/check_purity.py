#!/usr/bin/env python3
from pathlib import Path

# Runtime implementation files must stay assembly-only. Test, docs, and CI code
# are exempt because they are not shipped as the participant runtime.
FORBIDDEN_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cxx",
    ".rs", ".go", ".zig", ".cs", ".java",
    ".js", ".ts",
}
ALLOWED_DIRS = {"tests", "docs", ".github"}

violations = []
for path in Path(".").rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    if path.parts[0] in ALLOWED_DIRS:
        continue
    if path.suffix in FORBIDDEN_SUFFIXES:
        violations.append(str(path))

if violations:
    raise SystemExit("non-assembly implementation files found:\n" + "\n".join(violations))

print("purity check passed")
