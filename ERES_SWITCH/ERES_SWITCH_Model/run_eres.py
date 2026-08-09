from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = ROOT.parent
DEFAULT_BUNDLE = PACKAGE_ROOT / "ERES_Input_Data" / "global-input-bundle-v2"
DEFAULT_MODEL = ROOT / "model"
DEFAULT_SWITCH_SOURCE = ROOT / "vendor" / "SWITCH-2.0.9.post0"
PROFILE_RUNNER = ROOT / "tools" / "run_profiled_switch.py"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one registered ERES SWITCH scenario."
    )
    parser.add_argument("--scenario-profile", required=True)
    parser.add_argument("--carbon-case", required=True)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--switch-source-dir", type=Path, default=DEFAULT_SWITCH_SOURCE)
    parser.add_argument("--python-executable", type=Path, default=Path(sys.executable))
    parser.add_argument("--outputs-dir", type=Path)
    parser.add_argument("--work-dir", type=Path)
    args, switch_args = parser.parse_known_args()

    outputs = args.outputs_dir
    if outputs is None:
        outputs = (
            ROOT
            / "outputs"
            / args.scenario_profile
            / args.carbon_case
        )

    command = [
        str(args.python_executable.resolve()),
        str(PROFILE_RUNNER),
        "--bundle",
        str(args.bundle.resolve()),
        "--scenario-profile",
        args.scenario_profile,
        "--carbon-case",
        args.carbon_case,
        "--outputs-dir",
        str(outputs.resolve()),
        "--model-dir",
        str(args.model_dir.resolve()),
        "--switch-source-dir",
        str(args.switch_source_dir.resolve()),
        "--python-executable",
        str(args.python_executable.resolve()),
    ]
    if args.work_dir is not None:
        command.extend(["--work-dir", str(args.work_dir.resolve())])
    command.extend(switch_args)
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
