from __future__ import annotations

import argparse
import json
from pathlib import Path

from profiled_inputs import build_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--source-input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = build_bundle(
        args.source_manifest.resolve(),
        args.source_input_root.resolve(),
        args.output.resolve(),
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
