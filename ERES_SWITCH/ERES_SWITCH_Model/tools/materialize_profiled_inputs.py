from __future__ import annotations

import argparse
import json
from pathlib import Path

from profiled_inputs import materialize_inputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--scenario-profile", required=True)
    parser.add_argument("--carbon-case", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = materialize_inputs(
        args.bundle.resolve(),
        args.scenario_profile,
        args.carbon_case,
        args.output.resolve(),
    )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
