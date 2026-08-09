from __future__ import annotations

import csv
import importlib
import json
import sys
from importlib.util import find_spec
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = ROOT.parent
BUNDLE = PACKAGE_ROOT / "ERES_Input_Data" / "global-input-bundle-v2"
VENDOR = ROOT / "vendor" / "SWITCH-2.0.9.post0"


def module_version(name: str) -> str:
    module = importlib.import_module(name)
    return str(getattr(module, "__version__", "not reported"))


def main() -> int:
    sys.path.insert(0, str(VENDOR))
    versions = {
        name: module_version(name)
        for name in ("switch_model", "pyomo", "pandas", "numpy", "pint", "gurobipy")
    }
    # The 2.0.9.post0 distribution retains 2.0.9 in its source-level
    # switch_model.version module; setup.py adds the post-release suffix.
    if versions["switch_model"] != "2.0.9":
        raise RuntimeError(
            f"unexpected SWITCH version: {versions['switch_model']}"
        )

    with (BUNDLE / "scenario_manifest.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        scenarios = list(csv.DictReader(stream))
    profiles = sorted({row["scenario_profile"] for row in scenarios})
    storage_files = list(
        BUNDLE.glob("regions/*/eres/*/storage_energy_limits.csv")
    )
    gen_info_files = list(
        BUNDLE.glob("regions/*/profiles/*/gen_info.csv")
    )

    checks = {
        "pkg_resources_available": find_spec("pkg_resources") is not None,
        "scenario_count": len(scenarios),
        "profile_count": len(profiles),
        "storage_energy_limits_file_count": len(storage_files),
        "gen_info_file_count": len(gen_info_files),
    }
    passed = (
        checks["pkg_resources_available"]
        and checks["scenario_count"] == 315
        and checks["profile_count"] == 27
        and checks["storage_energy_limits_file_count"] == 9
        and checks["gen_info_file_count"] == 27
    )
    report = {
        "passed": passed,
        "python": sys.version.split()[0],
        "versions": versions,
        "checks": checks,
    }
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
