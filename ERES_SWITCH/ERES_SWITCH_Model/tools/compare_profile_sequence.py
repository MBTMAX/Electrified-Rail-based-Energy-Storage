from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


IGNORED_REPRODUCTION_FILES = {"model_config.json"}
IGNORED_REFERENCE_FILES = {"model_config.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_by_name(directory: Path) -> dict[str, Path]:
    return {
        path.relative_to(directory).as_posix(): path
        for path in directory.rglob("*")
        if path.is_file()
    }


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference-manifest",
        type=Path,
        required=True,
        help=(
            "Private validation manifest containing scenario_profile, "
            "carbon_case, scenario_name, and outputs_relative_path."
        ),
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--scenario-profile", required=True)
    parser.add_argument("--reproduction-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", required=True)
    args = parser.parse_args()

    manifest = read_manifest(args.reference_manifest)
    results = []
    for carbon_case in args.cases:
        rows = [
            row
            for row in manifest
            if row["scenario_profile"] == args.scenario_profile
            and row["carbon_case"] == carbon_case
        ]
        if len(rows) != 1:
            raise ValueError(
                f"expected one manifest row for "
                f"{args.scenario_profile} {carbon_case}, found {len(rows)}"
            )
        row = rows[0]
        reference = args.source_root / row["outputs_relative_path"]
        reproduction = args.reproduction_root / carbon_case
        reference_files = files_by_name(reference)
        reproduction_files = files_by_name(reproduction)
        comparable_reference = (
            set(reference_files) - IGNORED_REFERENCE_FILES
        )
        comparable_reproduction = (
            set(reproduction_files) - IGNORED_REPRODUCTION_FILES
        )
        missing = sorted(comparable_reference - comparable_reproduction)
        extra = sorted(comparable_reproduction - comparable_reference)
        common = sorted(
            comparable_reference & comparable_reproduction
        )
        mismatches = [
            filename
            for filename in common
            if sha256(reference_files[filename])
            != sha256(reproduction_files[filename])
        ]
        reference_cost = (
            reference / "total_cost.txt"
        ).read_text(encoding="utf-8").strip()
        reproduction_cost = (
            reproduction / "total_cost.txt"
        ).read_text(encoding="utf-8").strip()
        result = {
            "scenario_profile": args.scenario_profile,
            "carbon_case": carbon_case,
            "scenario_name": row["scenario_name"],
            "passed": (
                not missing
                and not extra
                and not mismatches
                and reference_cost == reproduction_cost
            ),
            "reference_outputs": str(reference),
            "reproduction_outputs": str(reproduction),
            "reference_output_file_count": len(reference_files),
            "reproduction_output_file_count": len(reproduction_files),
            "binary_identical_output_file_count": (
                len(common) - len(mismatches)
            ),
            "hash_mismatches": mismatches,
            "missing_in_reproduction": missing,
            "extra_in_reproduction": extra,
            "reference_total_cost": reference_cost,
            "reproduction_total_cost": reproduction_cost,
            "total_cost_exactly_equal": reference_cost == reproduction_cost,
            "intentionally_ignored_files": sorted(
                IGNORED_REFERENCE_FILES | IGNORED_REPRODUCTION_FILES
            ),
        }
        results.append(result)
        print(
            f"{args.scenario_profile} {carbon_case}: "
            f"{'PASS' if result['passed'] else 'FAIL'}",
            flush=True,
        )

    report = {
        "passed": len(results) == len(args.cases)
        and all(result["passed"] for result in results),
        "comparison_rule": (
            "SHA-256 exact equality for all model result files; "
            "model_config.json is intentionally excluded."
        ),
        "scenario_profile": args.scenario_profile,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
