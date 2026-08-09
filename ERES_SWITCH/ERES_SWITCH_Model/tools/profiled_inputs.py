"""Build and materialize the global profiled input bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path


PROFILE_FILES = (
    "gen_info.csv",
    "gen_build_costs.csv",
)
ERES_FILES = (
    "storage_energy_limits.csv",
)
STRUCTURAL_FILES = PROFILE_FILES + ERES_FILES
CARBON_FILE = "carbon_policies.csv"
PUBLIC_SCENARIO_FIELDS = (
    "scenario_name",
    "scenario_profile",
    "region",
    "eres_case",
    "tech_scenario",
    "carbon_case",
    "solver",
    "solver_options_string",
    "crossover",
)
CARBON_PATTERN = re.compile(r"_(\d{3})$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_profile(profile: str) -> tuple[str, str, str]:
    parts = profile.split("_")
    if (
        len(parts) != 3
        or parts[0] not in {"CN", "EU", "IN"}
        or parts[1] not in {"BR", "HR", "NR"}
        or parts[2] not in {"A", "C", "M"}
    ):
        raise ValueError(f"invalid scenario profile: {profile}")
    return parts[0], parts[1], parts[2]


def get_carbon_case(scenario_name: str) -> str:
    match = CARBON_PATTERN.search(scenario_name)
    return f"CE{match.group(1)}" if match else "BASELINE"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(
    path: Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_checksums(root: Path) -> None:
    manifest = root / "checksums.sha256"
    lines = []
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file() and item != manifest),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        lines.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}")
    with manifest.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines) + "\n")


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build_bundle(
    source_manifest: Path,
    source_input_root: Path,
    output: Path,
) -> dict:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"bundle output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    source_rows = read_csv(source_manifest)
    if len(source_rows) != 315:
        raise ValueError(
            f"expected 315 canonical scenarios, found {len(source_rows)}"
        )

    scenarios = []
    by_region: dict[str, list[dict]] = defaultdict(list)
    for source_row in source_rows:
        profile = source_row["scenario_profile"]
        region, eres_case, tech_scenario = parse_profile(profile)
        input_dir = source_input_root / source_row["inputs_relative_path"]
        if not input_dir.is_dir():
            raise FileNotFoundError(input_dir)
        files = {
            path.name: path
            for path in input_dir.iterdir()
            if path.is_file()
        }
        scenario = {
            **source_row,
            "region": region,
            "eres_case": eres_case,
            "tech_scenario": tech_scenario,
            "carbon_case": get_carbon_case(source_row["scenario_name"]),
            "input_dir": input_dir,
            "files": files,
        }
        scenarios.append(scenario)
        by_region[region].append(scenario)

    file_manifest_rows = []
    for scenario in scenarios:
        for filename, path in sorted(scenario["files"].items()):
            file_manifest_rows.append(
                {
                    "scenario_name": scenario["scenario_name"],
                    "scenario_profile": scenario["scenario_profile"],
                    "carbon_case": scenario["carbon_case"],
                    "filename": filename,
                    "sha256": sha256(path),
                }
            )

    for region, region_scenarios in sorted(by_region.items()):
        region_root = output / "regions" / region
        filename_sets = [set(item["files"]) for item in region_scenarios]
        if any(names != filename_sets[0] for names in filename_sets[1:]):
            raise ValueError(f"{region}: inconsistent input file names")

        common_names = []
        for filename in sorted(filename_sets[0]):
            if filename in STRUCTURAL_FILES or filename == CARBON_FILE:
                continue
            hashes = {
                sha256(scenario["files"][filename])
                for scenario in region_scenarios
            }
            if len(hashes) != 1:
                raise ValueError(
                    f"{region}: unexpected variable input file {filename}"
                )
            common_names.append(filename)
            copy_file(
                region_scenarios[0]["files"][filename],
                region_root / "common" / filename,
            )

        by_profile: dict[str, list[dict]] = defaultdict(list)
        for scenario in region_scenarios:
            by_profile[scenario["scenario_profile"]].append(scenario)

        for profile, profile_scenarios in sorted(by_profile.items()):
            profile_root = region_root / "profiles" / profile
            for filename in PROFILE_FILES:
                hashes = {
                    sha256(scenario["files"][filename])
                    for scenario in profile_scenarios
                }
                if len(hashes) != 1:
                    raise ValueError(
                        f"{profile}: {filename} changes across carbon cases"
                    )
                copy_file(
                    profile_scenarios[0]["files"][filename],
                    profile_root / filename,
                )

            seen_cases = set()
            for scenario in profile_scenarios:
                case = scenario["carbon_case"]
                if case in seen_cases:
                    raise ValueError(f"duplicate combination: {profile} {case}")
                seen_cases.add(case)
                copy_file(
                    scenario["files"][CARBON_FILE],
                    region_root / "carbon" / profile / f"{case}.csv",
                )

        by_eres_case: dict[str, list[dict]] = defaultdict(list)
        for scenario in region_scenarios:
            by_eres_case[scenario["eres_case"]].append(scenario)
        for eres_case, eres_scenarios in sorted(by_eres_case.items()):
            for filename in ERES_FILES:
                hashes = {
                    sha256(scenario["files"][filename])
                    for scenario in eres_scenarios
                }
                if len(hashes) != 1:
                    raise ValueError(
                        f"{region}_{eres_case}: {filename} changes "
                        "across technology or carbon cases"
                    )
                copy_file(
                    eres_scenarios[0]["files"][filename],
                    region_root / "eres" / eres_case / filename,
                )

        (region_root / "region_manifest.json").write_text(
            json.dumps(
                {
                    "region": region,
                    "scenario_count": len(region_scenarios),
                    "profile_count": len(by_profile),
                    "common_files": common_names,
                    "profile_files": list(PROFILE_FILES),
                    "eres_files": list(ERES_FILES),
                    "carbon_file": CARBON_FILE,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    public_scenario_rows = [
        {
            field: scenario[field]
            for field in PUBLIC_SCENARIO_FIELDS
        }
        for scenario in scenarios
    ]
    write_csv(
        output / "scenario_manifest.csv",
        public_scenario_rows,
        list(PUBLIC_SCENARIO_FIELDS),
    )
    write_csv(
        output / "file_manifest.csv",
        file_manifest_rows,
        [
            "scenario_name",
            "scenario_profile",
            "carbon_case",
            "filename",
            "sha256",
        ],
    )
    bundle_report = {
        "format": "ERES global profiled SWITCH input bundle",
        "format_version": 2,
        "scenario_count": len(scenarios),
        "profile_count": len(
            {scenario["scenario_profile"] for scenario in scenarios}
        ),
        "region_count": len(by_region),
        "regions": sorted(by_region),
        "profile_files": list(PROFILE_FILES),
        "eres_files": list(ERES_FILES),
        "carbon_file": CARBON_FILE,
    }
    (output / "bundle_manifest.json").write_text(
        json.dumps(bundle_report, indent=2) + "\n",
        encoding="utf-8",
    )
    write_checksums(output)
    return bundle_report


def select_scenario(
    bundle: Path,
    scenario_profile: str,
    carbon_case: str,
) -> dict[str, str]:
    parse_profile(scenario_profile)
    matches = [
        row
        for row in read_csv(bundle / "scenario_manifest.csv")
        if row["scenario_profile"] == scenario_profile
        and row["carbon_case"] == carbon_case
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one registered scenario for {scenario_profile} "
            f"{carbon_case}, found {len(matches)}"
        )
    return matches[0]


def materialize_inputs(
    bundle: Path,
    scenario_profile: str,
    carbon_case: str,
    output: Path,
) -> dict:
    scenario = select_scenario(bundle, scenario_profile, carbon_case)
    region, eres_case, _ = parse_profile(scenario_profile)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"materialized output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    region_root = bundle / "regions" / region
    for source in (region_root / "common").iterdir():
        if source.is_file():
            copy_file(source, output / source.name)
    for filename in PROFILE_FILES:
        copy_file(
            region_root / "profiles" / scenario_profile / filename,
            output / filename,
        )
    for filename in ERES_FILES:
        copy_file(
            region_root / "eres" / eres_case / filename,
            output / filename,
        )
    copy_file(
        region_root / "carbon" / scenario_profile / f"{carbon_case}.csv",
        output / CARBON_FILE,
    )

    expected_rows = [
        row
        for row in read_csv(bundle / "file_manifest.csv")
        if row["scenario_name"] == scenario["scenario_name"]
    ]
    expected = {row["filename"]: row["sha256"] for row in expected_rows}
    actual_paths = {
        path.name: path for path in output.iterdir() if path.is_file()
    }
    failures = []
    if set(actual_paths) != set(expected):
        failures.append(
            {
                "file_set_mismatch": {
                    "missing": sorted(set(expected) - set(actual_paths)),
                    "extra": sorted(set(actual_paths) - set(expected)),
                }
            }
        )
    for filename in sorted(set(actual_paths) & set(expected)):
        actual_hash = sha256(actual_paths[filename])
        if actual_hash != expected[filename]:
            failures.append(
                {
                    "filename": filename,
                    "expected_sha256": expected[filename],
                    "actual_sha256": actual_hash,
                }
            )
    if failures:
        raise ValueError(
            "materialized input verification failed: "
            + json.dumps(failures, ensure_ascii=False)
        )

    return {
        "passed": True,
        "scenario_name": scenario["scenario_name"],
        "scenario_profile": scenario_profile,
        "carbon_case": carbon_case,
        "region": region,
        "materialized_file_count": len(actual_paths),
        "canonical_run_configuration": {
            "solver": scenario["solver"],
            "solver_options_string": scenario["solver_options_string"],
            "crossover": int(scenario["crossover"]),
        },
        "files": {
            filename: expected[filename] for filename in sorted(expected)
        },
    }
