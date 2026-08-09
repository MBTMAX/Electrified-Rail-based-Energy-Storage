# ERES SWITCH model

This folder is the executable source package for the ERES simulations.
It includes:

- the SWITCH 2.0.9.post0 source snapshot in`vendor`;
- the exact module and solver configuration in `model`;
- scenario materialization and launch utilities in `tools`;
- an exact dependency specification and setup script.

The sibling `ERES_Input_Data` folder is required at run time.

## Set up

```bash
bash setup_environment.sh
./.conda-env/bin/python verify_installation.py
```

The setup script installs SWITCH from a temporary copy of the bundled source
rather than downloading another SWITCH version or modifying the checksummed
vendor snapshot.

## Run

```bash
./.conda-env/bin/python run_eres.py \
  --scenario-profile IN_BR_A \
  --carbon-case CE000
```

Use `--outputs-dir` and `--work-dir` to select other writable
locations. Run `python run_eres.py --help` for all wrapper options.
Arguments not recognized by the wrapper are forwarded to SWITCH.

## Validate all input combinations

```bash
./.conda-env/bin/python tools/validate_global_input_bundle.py \
  --bundle ../ERES_Input_Data/global-input-bundle-v2 \
  --output validation/all-inputs.json
```

Build one representative model for each of the nine profiles in a
region without calling the solver:

```bash
./.conda-env/bin/python tools/validate_model_builds.py \
  --region IN \
  --output validation/IN-model-builds.json
```

Run the publication carbon-case sequence for the default `IN_BR_A`
profile:

```bash
./.conda-env/bin/python tools/run_case_sequence.py \
  --output-root validation/IN_BR_A_outputs \
  --report validation/IN_BR_A_sequence.json
```

## Solver

reported runs used Gurobi 12.0.1 with the per-scenario options recorded
in the input bundle. A valid Gurobi license is required. Gurobi and its
license are not included.
