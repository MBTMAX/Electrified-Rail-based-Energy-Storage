from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from profiled_inputs import materialize_inputs


CODE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = CODE_ROOT.parent
DEFAULT_BUNDLE = PACKAGE_ROOT / "ERES_Input_Data" / "global-input-bundle-v2"
MODEL_DIR = CODE_ROOT / "model"
SWITCH_SOURCE = CODE_ROOT / "vendor" / "SWITCH-2.0.9.post0"
BUILD_TEST = CODE_ROOT / "tools" / "build_model_test.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def representatives(bundle: Path, region: str) -> list[dict[str, str]]:
    rows = [
        row
        for row in read_rows(bundle / "scenario_manifest.csv")
        if row["region"] == region
    ]
    by_profile: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_profile.setdefault(row["scenario_profile"], []).append(row)

    selected = []
    for profile, candidates in sorted(by_profile.items()):
        preferred_case = "BASELINE" if "_NR_" in profile else "CE000"
        matches = [
            row for row in candidates
            if row["carbon_case"] == preferred_case
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{profile}: expected one representative "
                f"for {preferred_case}, found {len(matches)}"
            )
        selected.append(matches[0])
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--region", choices=("CN", "EU", "IN"), default="IN"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path)
    args = parser.parse_args()

    bundle = args.bundle.resolve()
    work_dir = (
        args.work_dir.resolve()
        if args.work_dir
        else CODE_ROOT / ".work" / "model-builds"
    )
    work_dir.mkdir(parents=True, exist_ok=True)
    result_dir = work_dir / "results"
    result_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    python_paths = [str(MODEL_DIR), str(SWITCH_SOURCE)]
    if environment.get("PYTHONPATH"):
        python_paths.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(python_paths)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["TMPDIR"] = str(work_dir)

    results = []
    started = time.perf_counter()
    selected = representatives(bundle, args.region)
    for row in selected:
        profile = row["scenario_profile"]
        carbon_case = row["carbon_case"]
        with tempfile.TemporaryDirectory(
            prefix=f"{profile}-", dir=work_dir
        ) as temporary:
            inputs = Path(temporary) / row["scenario_name"]
            materialize_inputs(bundle, profile, carbon_case, inputs)
            detail_path = result_dir / f"{profile}.json"
            command = [
                sys.executable,
                str(BUILD_TEST),
                "--inputs",
                str(inputs),
                "--profile",
                profile,
                "--carbon-case",
                carbon_case,
                "--output",
                str(detail_path),
            ]
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            result = {
                "scenario_profile": profile,
                "carbon_case": carbon_case,
                "scenario_name": row["scenario_name"],
                "passed": completed.returncode == 0,
                "returncode": completed.returncode,
            }
            if detail_path.is_file():
                detail = json.loads(detail_path.read_text(encoding="utf-8"))
                result["model_build"] = detail
                result["passed"] = result["passed"] and detail["passed"]
            else:
                result["stdout"] = completed.stdout[-4000:]
                result["stderr"] = completed.stderr[-4000:]
            results.append(result)
            print(
                f"{profile} {carbon_case}: "
                f"{'PASS' if result['passed'] else 'FAIL'}",
                flush=True,
            )

    report = {
        "passed": len(results) == 9
        and all(result["passed"] for result in results),
        "profile_count": len(results),
        "region": args.region,
        "input_source": str(bundle),
        "elapsed_seconds": time.perf_counter() - started,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
