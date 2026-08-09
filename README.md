# Transforming electrified railway into mechanical energy storage for energy transition

This repository provides the code, model configuration, and system
inputs used for the ERES capacity and SWITCH calculations reported in the
research article.

## Repository structure

```text
.
|-- ERES_Capacity_Optimization/
|   |-- run_ERES_case.m
|   |-- DEP_evaluation.m
|   |-- Aggregation_model.m
|   `-- README.md
|-- ERES_SWITCH/
|   |-- ERES_SWITCH_Model/
|   |-- ERES_Input_Data/
|   |-- verify_checksums.py
|   `-- README.md
`-- README.md
```

- `ERES_Capacity_Optimization` contains the MATLAB implementation used to
  calculate ERES charge, discharge, and energy capacities from railway
  operation inputs.
- `ERES_SWITCH` contains the complete SWITCH 2.0.9.post0 configuration,
  model extensions, scenario tools, and system input bundle.

## Railway-side ERES capacity calculation

The complete model-ready dataset contains 2,688 self-contained regional
timetable cases and is distributed separately because of its size.

**Data repository:** [Zenodo](https://doi.org/10.5281/zenodo.21736268)

The data are distributed across 12 ZIP archives, with 224 cases in each
archive. Download and extract all 12 archives into the same destination to
obtain the following layout:

```text
cases/
|-- Case_0001.mat
|-- ...
`-- Case_2688.mat
```

The tested environment is MATLAB R2023b, YALMIP 20230622, and Gurobi
Optimizer 11.0.2 on Windows 10. A valid Gurobi license is required.

From the repository root:

```matlab
addpath("ERES_Capacity_Optimization")
check_environment

dataRoot = "path/to/extracted/data";
caseFile = fullfile(dataRoot, "cases", "Case_0001.mat");
Result = run_ERES_case(caseFile);

Result.Discharge.PowerCapacity
Result.Discharge.EnergyCapacity
Result.Charge.PowerCapacity
Result.Charge.EnergyCapacity
Result.EnergyStorageCapacity
```

The bundled example and detailed field definitions are documented in
[`ERES_Capacity_Optimization/README.md`](ERES_Capacity_Optimization/README.md).

## SWITCH calculations

The SWITCH package includes the complete input bundle and canonical
configuration for 315 scenarios covering China, Europe, and India.

On a Linux system with Conda, Mamba, or Micromamba:

```bash
cd ERES_SWITCH
python verify_checksums.py

cd ERES_SWITCH_Model
bash setup_environment.sh
./.conda-env/bin/python verify_installation.py
./.conda-env/bin/python run_eres.py \
  --scenario-profile IN_BR_A \
  --carbon-case CE000
```

The reported SWITCH calculations used Python 3.13.3, SWITCH
2.0.9.post0, Pyomo 6.9.1, and Gurobi 12.0.1. A valid Gurobi license is
required. The scenario manifest and per-file checksums are included in the
input bundle.

Detailed setup, validation, and execution instructions are provided in
[`ERES_SWITCH/README.md`](ERES_SWITCH/README.md) and
[`ERES_SWITCH/ERES_SWITCH_Model/README.md`](ERES_SWITCH/ERES_SWITCH_Model/README.md).

## Licenses

The ERES capacity optimization code is released under the MIT License. The
SWITCH package includes the applicable third-party license texts and notices
in `ERES_SWITCH/ERES_SWITCH_Model`.
