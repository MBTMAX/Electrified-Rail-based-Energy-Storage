from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

from profiled_inputs import materialize_inputs, read_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    bundle = args.bundle.resolve()
    scenarios = read_csv(bundle / "scenario_manifest.csv")
    results = []
    started = time.perf_counter()
    for index, scenario in enumerate(scenarios, start=1):
        with tempfile.TemporaryDirectory(
            prefix="eres-bundle-validation-"
        ) as temp:
            try:
                detail = materialize_inputs(
                    bundle,
                    scenario["scenario_profile"],
                    scenario["carbon_case"],
                    Path(temp),
                )
                results.append(
                    {
                        "scenario_name": scenario["scenario_name"],
                        "scenario_profile": scenario["scenario_profile"],
                        "carbon_case": scenario["carbon_case"],
                        "passed": detail["passed"],
                        "materialized_file_count": detail[
                            "materialized_file_count"
                        ],
                    }
                )
            except Exception as error:
                results.append(
                    {
                        "scenario_name": scenario["scenario_name"],
                        "scenario_profile": scenario["scenario_profile"],
                        "carbon_case": scenario["carbon_case"],
                        "passed": False,
                        "error": str(error),
                    }
                )
        if index % 25 == 0 or index == len(scenarios):
            print(f"validated {index}/{len(scenarios)}", flush=True)

    report = {
        "passed": len(results) == 315
        and all(result["passed"] for result in results),
        "scenario_count": len(results),
        "elapsed_seconds": time.perf_counter() - started,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
