# ERES reproducibility package

This package provides the model code and input data for the SWITCH
simulations reported in "Transforming electrified railway into
mechanical energy storage for energy transition".

It is deliberately divided into two independent folders:

- `ERES_Input_Data`: the versioned global input bundle.
- `ERES_SWITCH_Model`: SWITCH 2.0.9.post0 source, ERES extensions,
  run configuration, environment specification, and launch tools.

Keep the two folders together because the model launcher locates the
input bundle through their sibling directory layout.

## Quick start

On a Linux system with Conda, Mamba, or Micromamba:

```bash
cd ERES_SWITCH_Model
bash setup_environment.sh
./.conda-env/bin/python verify_installation.py
./.conda-env/bin/python run_eres.py \
  --scenario-profile IN_BR_A \
  --carbon-case CE000
```

The last command writes a new output directory under
`ERES_SWITCH_Model/outputs`. Existing outputs are never overwritten.

Gurobi 12.0.1 and a valid Gurobi license are required to reproduce the
reported optimization results. The solver and its license are not
redistributed by this package.

Run `python verify_checksums.py` from this directory to verify both
folders before use.
