from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


CODE_ROOT = Path(__file__).resolve().parents[1]
RUNNER = CODE_ROOT / "run_eres.py"
DEFAULT_CASES = [
    *(f"CE{index:03d}" for index in range(16)),
    "CE105",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-profile", default="IN_BR_A")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--cases", nargs="+", default=DEFAULT_CASES)
    args = parser.parse_args()

    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    work_dir = (
        args.work_dir.resolve()
        if args.work_dir
        else CODE_ROOT / ".work" / "solves"
    )
    work_dir.mkdir(parents=True, exist_ok=True)
    results = []
    sequence_started = time.perf_counter()

    for carbon_case in args.cases:
        outputs = output_root / carbon_case
        stdout_path = output_root / f"{carbon_case}.stdout.log"
        stderr_path = output_root / f"{carbon_case}.stderr.log"
        started = time.perf_counter()
        command = [
            sys.executable,
            str(RUNNER),
            "--scenario-profile",
            args.scenario_profile,
            "--carbon-case",
            carbon_case,
            "--outputs-dir",
            str(outputs),
            "--work-dir",
            str(work_dir),
        ]
        with stdout_path.open("w", encoding="utf-8") as stdout:
            with stderr_path.open("w", encoding="utf-8") as stderr:
                completed = subprocess.run(
                    command,
                    stdout=stdout,
                    stderr=stderr,
                    check=False,
                )
        result = {
            "scenario_profile": args.scenario_profile,
            "carbon_case": carbon_case,
            "passed": completed.returncode == 0,
            "returncode": completed.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "outputs_dir": str(outputs),
        }
        results.append(result)
        report = {
            "passed": False,
            "complete": False,
            "scenario_profile": args.scenario_profile,
            "requested_cases": args.cases,
            "results": results,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"{args.scenario_profile} {carbon_case}: "
            f"{'PASS' if result['passed'] else 'FAIL'} "
            f"({result['elapsed_seconds']:.1f} s)",
            flush=True,
        )
        if not result["passed"]:
            break

    report = {
        "passed": len(results) == len(args.cases)
        and all(result["passed"] for result in results),
        "complete": len(results) == len(args.cases),
        "scenario_profile": args.scenario_profile,
        "requested_cases": args.cases,
        "elapsed_seconds": time.perf_counter() - sequence_started,
        "results": results,
    }
    args.report.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
