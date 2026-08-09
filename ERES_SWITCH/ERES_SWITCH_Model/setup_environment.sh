#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="$ROOT/.conda-env"

if command -v micromamba >/dev/null 2>&1; then
    MANAGER=(micromamba)
elif command -v mamba >/dev/null 2>&1; then
    MANAGER=(mamba)
elif command -v conda >/dev/null 2>&1; then
    MANAGER=(conda)
else
    echo "Conda, Mamba, or Micromamba is required." >&2
    exit 2
fi

if [[ -e "$PREFIX" ]]; then
    echo "Refusing to overwrite existing environment: $PREFIX" >&2
    exit 3
fi

"${MANAGER[@]}" env create --prefix "$PREFIX" --file "$ROOT/environment.yml"

# Build from a temporary copy so pip cannot add build metadata to the
# checksummed vendor source snapshot.
BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/eres-switch-install.XXXXXX")"
trap 'rm -rf "$BUILD_ROOT"' EXIT
cp -a "$ROOT/vendor/SWITCH-2.0.9.post0" "$BUILD_ROOT/"
"$PREFIX/bin/python" -m pip install --no-deps \
    "$BUILD_ROOT/SWITCH-2.0.9.post0"
"$PREFIX/bin/python" "$ROOT/verify_installation.py"

echo "Environment ready: $PREFIX"
