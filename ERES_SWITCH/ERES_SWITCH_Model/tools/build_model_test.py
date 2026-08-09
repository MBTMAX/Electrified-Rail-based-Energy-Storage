from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


CODE_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = CODE_ROOT / "model"
SWITCH_SOURCE = CODE_ROOT / "vendor" / "SWITCH-2.0.9.post0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--carbon-case", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    inputs_dir = args.inputs.resolve()
    sys.path.insert(0, str(SWITCH_SOURCE))
    sys.path.insert(0, str(MODEL_DIR))
    os.chdir(MODEL_DIR)

    from switch_model import solve

    switch_args = solve.get_option_file_args(
        dir=str(MODEL_DIR),
        extra_args=[
            "--inputs-dir",
            str(inputs_dir),
            "--outputs-dir",
            str(args.output.parent / "build-only-unused"),
            "--scenario-profile",
            args.profile,
            "--carbon-case",
            args.carbon_case,
            "--no-post-solve",
        ],
    )

    started = time.perf_counter()
    instance = solve.main(args=switch_args, return_instance=True)
    elapsed = time.perf_counter() - started

    expected_components = {
        "Enforce_Storage_Energy_Limit": True,
        "Enforce_Capacity_Plan": False,
        "Enforce_Total_Capacity_Limit": True,
    }
    component_checks = {
        name: {
            "exists": hasattr(instance, name),
            "indexed_size": (
                len(getattr(instance, name))
                if hasattr(instance, name)
                else 0
            ),
        }
        for name in expected_components
    }
    failures = [
        f"missing or empty model component: {name}"
        for name, check in component_checks.items()
        if not check["exists"]
        or (expected_components[name] and check["indexed_size"] == 0)
    ]

    report = {
        "passed": not failures,
        "test_type": "model definition, input load, and pre-solve only",
        "solver_called": False,
        "elapsed_seconds": elapsed,
        "scenario_profile": args.profile,
        "carbon_case": args.carbon_case,
        "generation_project_count": len(instance.GENERATION_PROJECTS),
        "storage_project_count": len(instance.STORAGE_GENS),
        "component_checks": component_checks,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
