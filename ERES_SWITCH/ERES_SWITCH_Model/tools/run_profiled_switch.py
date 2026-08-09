from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from profiled_inputs import materialize_inputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--scenario-profile", required=True)
    parser.add_argument("--carbon-case", required=True)
    parser.add_argument("--outputs-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument(
        "--work-dir",
        type=Path,
        help="Optional parent directory for temporary inputs and solver files.",
    )
    parser.add_argument(
        "--switch-executable",
        type=Path,
        help=(
            "Optional installed Switch command. When omitted, the runner "
            "uses '<python> -m switch_model.main solve'."
        ),
    )
    parser.add_argument(
        "--python-executable",
        type=Path,
        default=Path(sys.executable),
        help="Python interpreter used for the bundled Switch source.",
    )
    parser.add_argument(
        "--switch-source-dir",
        type=Path,
        help=(
            "Directory containing the bundled switch_model package. "
            "Added to PYTHONPATH ahead of installed packages."
        ),
    )
    args, switch_args = parser.parse_known_args()

    bundle = args.bundle.resolve()
    outputs = args.outputs_dir.resolve()
    model_dir = args.model_dir.resolve()
    work_dir = args.work_dir.resolve() if args.work_dir else None
    if outputs.exists():
        raise FileExistsError(f"refusing to overwrite outputs: {outputs}")
    if work_dir is not None:
        work_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="eres-profiled-inputs-",
        dir=work_dir,
    ) as temp:
        materialized = Path(temp)
        report = materialize_inputs(
            bundle,
            args.scenario_profile,
            args.carbon_case,
            materialized,
        )
        canonical = report["canonical_run_configuration"]
        if args.switch_executable is not None:
            switch_command = [
                str(args.switch_executable.resolve()),
                "solve",
            ]
        else:
            switch_command = [
                str(args.python_executable.resolve()),
                "-m",
                "switch_model.main",
                "solve",
            ]
        command = [
            *switch_command,
            "--inputs-dir",
            str(materialized),
            "--outputs-dir",
            str(outputs),
            "--scenario-name",
            report["scenario_name"],
            "--scenario-profile",
            args.scenario_profile,
            "--carbon-case",
            args.carbon_case,
            "--solver",
            canonical["solver"],
            "--solver-options-string",
            canonical["solver_options_string"],
            *switch_args,
        ]
        environment = os.environ.copy()
        environment["PYTHONNOUSERSITE"] = "1"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        python_paths = [str(model_dir)]
        if args.switch_source_dir is not None:
            python_paths.append(str(args.switch_source_dir.resolve()))
        if environment.get("PYTHONPATH"):
            python_paths.append(environment["PYTHONPATH"])
        environment["PYTHONPATH"] = os.pathsep.join(python_paths)
        if work_dir is not None:
            environment["TMPDIR"] = str(work_dir)
        completed = subprocess.run(
            command,
            cwd=model_dir,
            env=environment,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
