#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/.conda-env/bin/python" "$ROOT/run_eres.py" \
    --scenario-profile IN_BR_A \
    --carbon-case CE000 \
    "$@"
