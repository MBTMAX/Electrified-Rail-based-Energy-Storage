from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNTIME_DIRECTORIES = {
    ".conda-env",
    ".work",
    "outputs",
    "validation",
    "__pycache__",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(folder: Path) -> list[str]:
    manifest = folder / "checksums.sha256"
    expected = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            checksum, relative_path = line.split("  ", 1)
            expected[relative_path] = checksum
    actual = {}
    for path in folder.rglob("*"):
        if not path.is_file() or path == manifest:
            continue
        relative = path.relative_to(folder)
        if any(part in RUNTIME_DIRECTORIES for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        actual[relative.as_posix()] = path
    failures = []
    for relative_path in sorted(expected.keys() | actual.keys()):
        if relative_path not in expected:
            failures.append(f"{folder.name}: unexpected {relative_path}")
        elif relative_path not in actual:
            failures.append(f"{folder.name}: missing {relative_path}")
        elif sha256(actual[relative_path]) != expected[relative_path]:
            failures.append(f"{folder.name}: mismatch {relative_path}")
    return failures


def main() -> int:
    folders = [ROOT / "ERES_Input_Data", ROOT / "ERES_SWITCH_Model"]
    failures = [failure for folder in folders for failure in verify(folder)]
    if failures:
        print("\n".join(failures))
        return 1
    print("Verified both package folders.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
