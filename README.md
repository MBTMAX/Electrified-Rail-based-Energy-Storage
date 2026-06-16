# Electrified Rail-based Energy Storage

This repository provides MATLAB code and example data for evaluating the capacity of electrified rail-based energy storage (ERES) from railway operation data. The example demonstrates how the power regulation potential of inter-stop operation records are optimized, parameterized and aggregated.

The code accompanies the research article:

**Transforming electrified railway into mechanical energy storage for energy transition**

## 1. Repository scope

This repository focuses on the ERES capacity evaluation workflow. The public MATLAB example demonstrates how to:

1. load inter-stop operation data;
2. evaluate deployable ERES power and energy for a specified regulation setting;
3. repeat the evaluation over multiple regulation durations;
4. evaluate discharge and charge regulation separately;
5. aggregate the resulting regulation capability into an equivalent energy storage; and
6. plot the bidirectional regulation deployable region.

The provided public dataset, `TrainConfiguration_example.mat`, contains 50 anonymized inter-stop operation records. Users can replace this file with data in the same structure to evaluate other train-operation cases.

In the article, the full assessment uses a much larger railway operation dataset and subsequent power system planning analyses. The MATLAB scripts in this repository are intended to make the railway-side capacity evaluation procedure transparent and executable on a small public example. They are not intended to reproduce every numerical result in the manuscript directly from the 50-record example dataset.

The subsequent power system planning simulations in the manuscript were performed with SWITCH, an open-source capacity expansion model, using ERES capacity bounds and techno-economic assumptions derived from the railway-side assessment. This repository does not redistribute the SWITCH source code. Users who wish to inspect or extend the power system planning component should use the SWITCH together with the model settings and assumptions described in the manuscript and Supplementary Information.

## 2. Correspondence with the manuscript workflow

The public MATLAB example corresponds to the railway-side ERES capacity evaluation part of the manuscript. The relationship between the manuscript workflow and the public code is summarized below.

| Manuscript / Supplementary Information step | Public code coverage |
|---|---|
| Loading inter-stop operation records and mapped train/line parameters | `TrainConfiguration_example.mat` and `Example.m` |
| Evaluating deployable regulation power under one duration, start time and direction | `DEP_evaluation.m` |
| Repeating the evaluation over multiple prescribed regulation durations | Multi-duration loops in `Example.m` |
| Evaluating discharge and charge regulation separately | `RegSet{4}=1` for discharge and `RegSet{4}=2` for charge |
| Converting multi-duration regulation results into an equivalent energy storage | `Aggregation_model.m` |
| Combining fitted discharge and charge energy capacities | `ESC_dis + ESC_cha` in `Example.m` |
| Plotting the bidirectional deployable region | `PlotResult.m` |


## 3. Software requirements

The MATLAB code uses YALMIP with Gurobi as the optimization solver.

The code was tested under the following environment:

| Component | Tested version |
|---|---|
| MATLAB | `R2023b` |
| YALMIP | `R20250626` |
| Gurobi Optimizer | `11.0.2` |
| Operating system | `Windows 10` |

Required software:

- MATLAB;
- YALMIP;
- Gurobi Optimizer;
- a valid Gurobi license;
- the MATLAB interface for Gurobi.

The optimization problem in `DEP_evaluation.m` is formulated through YALMIP and solved using Gurobi. Therefore, both YALMIP and Gurobi must be installed and available on the MATLAB path before running the example. No non-standard hardware is required. The demo can be run on a standard desktop/laptop computer.

## 4. Repository files

| File | Description |
|---|---|
| `Example.m` | Main example script. It demonstrates the main workflow, including single-period deployable ERES regulation optimization, multi-duration discharge and charge evaluation, storage-equivalent aggregation, and bidirectional plotting. |
| `DEP_evaluation.m` | Function for evaluating deployable ERES power and delivered regulation energy for selected inter-stop operation records under a specified regulation duration, regulation direction, and start time. |
| `Aggregation_model.m` | Function for converting deployable power results over multiple regulation durations into an aggregated storage-equivalent model. |
| `PlotResult.m` | Function for plotting the bidirectional discharge and charge regulation deployable regions and deployable power results. |
| `check_environment.m` | Utility script for checking whether the required MATLAB functions, YALMIP, and Gurobi are available. |
| `TrainConfiguration_example.mat` | Example dataset containing 50 anonymized inter-stop operation records. |
| `LICENSE` | Repository license file. |
| `README.md` | This documentation file. |

The variable and file name `TrainConfiguration` is retained for compatibility with the original implementation. In the context of this repository, each element of `TrainConfiguration` corresponds to one inter-stop operation record rather than an entire daily train service.

## 5. Installation and setup

The demo requires no additional installation and normally takes less than 5 minutes to set up. Installing MATLAB, YALMIP and Gurobi may take longer depending on the local environment.

### Step 1. Clone or download the repository

Using Git:

```bash
git clone https://github.com/MBTMAX/Electrified-Rail-based-Energy-Storage.git
cd Electrified-Rail-based-Energy-Storage
```

Alternatively, download the repository as a ZIP file from GitHub and extract it.

### Step 2. Open MATLAB

Start MATLAB and set the repository folder as the current working directory.

For example:

```matlab
cd('path/to/Electrified-Rail-based-Energy-Storage')
```

### Step 3. Add the repository to the MATLAB path

```matlab
addpath(genpath(pwd))
```

### Step 4. Make sure YALMIP and Gurobi are available

YALMIP and Gurobi must be installed separately.

After installing YALMIP, add it to the MATLAB path. For example:

```matlab
addpath(genpath('path/to/yalmip'))
```

Gurobi should also be correctly linked to MATLAB. Depending on the installation method, this can usually be checked by running:

```matlab
which gurobi
```

If Gurobi provides a setup script for the local installation, run the corresponding setup command following the Gurobi documentation.

### Step 5. Run the environment check

From the repository root folder, run:

```matlab
check_environment
```

A successful check should confirm that the required repository files, YALMIP functions, and Gurobi solver are available.

If the environment check fails, see the troubleshooting section below.

## 6. Quick start

To run the public example, execute:

```matlab
Example
```

The script performs three main tasks:

1. evaluates deployable ERES power and delivered regulation energy for a 5-minute discharge regulation case starting at 10:00;
2. repeats the multi-duration evaluation separately for discharge and charge regulation over regulation durations from 0 to 15 minutes; and
3. builds and plots the bidirectional aggregated equivalent energy storage.

The example uses the following regulation setting for the single-period discharge demonstration:

```matlab
RegSet{1} = 1:50;       % indices of participating inter-stop operation records
RegSet{2} = 60;         % discrete time step, s
RegSet{3} = [0 5];      % regulation duration, min
RegSet{4} = 1;          % regulation direction: 1 discharge, 2 charge
RegSet{5} = 36000;      % regulation start time, s from the beginning of the day
```

Expected screen output should include the single-period deployable discharge power and delivered regulation energy, the aggregated discharge power capacity, the aggregated charge power capacity, and the bidirectional aggregated ERES storage capacity.

For the tested environment, the public example produced:

```text
Single-period deployable power: 106.020494 MW
Single-period deployable energy: 8.835041 MWh
Aggregated ERES discharge power capacity: 511.699192 MW
Aggregated ERES charge power capacity: 388.191922 MW
Aggregated ERES storage capacity: 21.183548 MWh
```

Small numerical differences may occur across MATLAB, YALMIP, or Gurobi versions because the optimization problem can have multiple numerically equivalent solutions. The demo is expected to finish within several minutes on a standard desktop computer.

The script also generates a figure showing the bidirectional regulation deployable region. Charge regulation is plotted as positive power, and discharge regulation is plotted as negative power.

## 7. Workflow description

The public example follows the workflow below.

### 7.1 Deployable ERES regulation optimization

The first part of `Example.m` loads the example inter-stop operation data and evaluates deployable ERES power and delivered regulation energy for one regulation setting.

```matlab
load('TrainConfiguration_example.mat');
TrainConfiguration = TrainConfiguration_example;

RegSet{1} = 1:50;
RegSet{2} = 60;
RegSet{3} = [0 5];
RegSet{4} = 1;
RegSet{5} = 36000;

[Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);
```

Outputs:

| Output | Meaning | Unit |
|---|---|---|
| `Power` | Deployable ERES power over the specified regulation duration | MW |
| `Energy` | Delivered regulation energy over the specified regulation duration | MWh |
| `ChangeofPower` | Power adjustment profile of each participating inter-stop operation record | MW |

### 7.2 Multi-duration capacity evaluation

The second part of `Example.m` repeats the deployable regulation evaluation for regulation durations from 0 to 15 minutes. Discharge and charge regulation are evaluated separately.

For discharge regulation:

```matlab
RegSet{4} = 1;

Power_MultiplePeriod_dis = zeros(size(RegDeployingPeriod_MultiplePeriod));
Energy_MultiplePeriod_dis = zeros(size(RegDeployingPeriod_MultiplePeriod));
ChangeofPower_MultiplePeriod_dis = cell(size(RegDeployingPeriod_MultiplePeriod));

for k = 1:length(RegDeployingPeriod_MultiplePeriod)
    RegDeployingPeriod = RegDeployingPeriod_MultiplePeriod(k);
    RegSet{3} = [0 RegDeployingPeriod];

    [Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);

    Power_MultiplePeriod_dis(k) = Power;
    Energy_MultiplePeriod_dis(k) = Energy;
    ChangeofPower_MultiplePeriod_dis{k} = ChangeofPower;
end
```

For charge regulation:

```matlab
RegSet{4} = 2;

Power_MultiplePeriod_cha = zeros(size(RegDeployingPeriod_MultiplePeriod));
Energy_MultiplePeriod_cha = zeros(size(RegDeployingPeriod_MultiplePeriod));
ChangeofPower_MultiplePeriod_cha = cell(size(RegDeployingPeriod_MultiplePeriod));

for k = 1:length(RegDeployingPeriod_MultiplePeriod)
    RegDeployingPeriod = RegDeployingPeriod_MultiplePeriod(k);
    RegSet{3} = [0 RegDeployingPeriod];

    [Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);

    Power_MultiplePeriod_cha(k) = Power;
    Energy_MultiplePeriod_cha(k) = Energy;
    ChangeofPower_MultiplePeriod_cha{k} = ChangeofPower;
end
```

Outputs:

| Output | Meaning |
|---|---|
| `Power_MultiplePeriod_dis` | Deployable discharge power for each tested regulation duration |
| `Energy_MultiplePeriod_dis` | Delivered discharge regulation energy for each tested regulation duration |
| `ChangeofPower_MultiplePeriod_dis` | Discharge power-adjustment results for each tested regulation duration |
| `Power_MultiplePeriod_cha` | Deployable charge power for each tested regulation duration |
| `Energy_MultiplePeriod_cha` | Delivered charge regulation energy for each tested regulation duration |
| `ChangeofPower_MultiplePeriod_cha` | Charge power-adjustment results for each tested regulation duration |

The public script assumes that `RegDeployingPeriod_MultiplePeriod` is a vector of non-negative integer-minute durations beginning at zero. If arbitrary duration values are used, the indexing in the loop should be modified accordingly.

### 7.3 Aggregated storage-equivalent model

The deployable power results across multiple regulation durations are converted into storage-equivalent models separately for discharge and charge regulation.

```matlab
[EPC_dis, ESC_dis, RDR_dis] = Aggregation_model(ChangeofPower_MultiplePeriod_dis, RegDeployingPeriod_MultiplePeriod);
[EPC_cha, ESC_cha, RDR_cha] = Aggregation_model(ChangeofPower_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod);
```

Outputs:

| Output | Meaning | Unit |
|---|---|---|
| `EPC_dis` | Aggregated discharge power capacity | MW |
| `ESC_dis` | Fitted discharge-side storage-equivalent energy capacity | MWh |
| `RDR_dis` | Discharge regulation deployable region | min and MW |
| `EPC_cha` | Aggregated charge power capacity | MW |
| `ESC_cha` | Fitted charge-side storage-equivalent energy capacity | MWh |
| `RDR_cha` | Charge regulation deployable region | min and MW |

The bidirectional ERES storage capacity reported by the public example is calculated as:

```matlab
ESC_total = ESC_dis + ESC_cha;
```

Discharge and charge power capacities are reported separately because the two directions have different feasible power limits and baseline operating states.

### 7.4 Plotting

The final part of `Example.m` plots the bidirectional regulation deployable region.

```matlab
PlotResult(RDR_dis, Power_MultiplePeriod_dis, RDR_cha, Power_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod);
```

The plot uses the following sign convention:

| Regulation direction | Plot sign | Physical meaning |
|---|---|---|
| Charge | Positive | Additional electrical power absorbed by trains |
| Discharge | Negative | Reduced net traction demand or regenerative output |

The sign convention is used only for visualization. The numerical outputs of `DEP_evaluation.m` and `Aggregation_model.m` are reported as positive magnitudes for each evaluated direction.

## 8. Main input settings

The regulation case is controlled by the cell array `RegSet`.

| Variable | Meaning | Example |
|---|---|---|
| `RegSet{1}` | Indices of participating inter-stop operation records | `1:50` |
| `RegSet{2}` | Discrete time step | `60` s |
| `RegSet{3}` | Regulation duration | `[0 5]` min |
| `RegSet{4}` | Regulation direction | `1` discharge, `2` charge |
| `RegSet{5}` | Regulation start time | `36000` s |

### 8.1 Change the participating operation records

To evaluate only the first 20 inter-stop operation records:

```matlab
RegSet{1} = 1:20;
```

To evaluate a selected subset:

```matlab
RegSet{1} = [1 5 8 12 20];
```

The indices in `RegSet{1}` refer to elements of `TrainConfiguration`.

### 8.2 Change the regulation duration

`RegSet{3}` defines the regulation duration in the form `[0 duration_min]`. In the current implementation, the first element should be zero. The regulation start time is controlled separately by `RegSet{5}`.

To evaluate a 10-minute regulation case:

```matlab
RegSet{3} = [0 10];
```

Do not use `RegSet{3} = [5 10]` to represent a regulation interval from minute 5 to minute 10. To change the absolute start time of the regulation request, modify `RegSet{5}`.

To evaluate multiple durations from 0 to 20 minutes in the aggregation workflow:

```matlab
RegDeployingPeriod_MultiplePeriod = 0:20;
```

The public example assumes integer-minute regulation durations. If a non-integer duration resolution is required, both the loop indexing in `Example.m` and the duration handling in `DEP_evaluation.m` should be modified consistently.

### 8.3 Change the regulation direction

For discharge regulation:

```matlab
RegSet{4} = 1;
```

For charge regulation:

```matlab
RegSet{4} = 2;
```

In this repository, discharge and charge regulation are evaluated separately because the feasible power adjustment depends on the scheduled operating condition, traction power limits, regenerative braking limits, and the regulation direction.

### 8.4 Change the regulation start time

The regulation start time is given in seconds from the beginning of the day.

For example, 10:00 is:

```matlab
RegSet{5} = 36000;
```

For 12:00:

```matlab
RegSet{5} = 43200;
```

For 18:00:

```matlab
RegSet{5} = 64800;
```

The selected start time should overlap with the admissible regulation windows of at least some operation records. Otherwise, the deployable power and energy may be zero.

### 8.5 Change the discrete time step

The public example uses:

```matlab
RegSet{2} = 60;
```

The current example workflow assumes a 60-second time step. This assumption is also used in the multi-duration aggregation because one column of `ChangeofPower` corresponds to one minute. Users should keep `RegSet{2} = 60` unless they also modify the indexing and duration handling in `Example.m`, `DEP_evaluation.m`, and `Aggregation_model.m` consistently.

## 9. Input data structure

The input variable `TrainConfiguration` is a `1 × N` structure array, where `N` is the number of inter-stop operation records.

Each element of `TrainConfiguration` corresponds to one scheduled movement between two stopping events and contains the following fields.

| Field | Type | Description | Unit |
|---|---|---|---|
| `TrainPara` | `1 × 10` double | Train physical and efficiency parameters | mixed |
| `RoadPara` | `m × 2` double | Track-segment speed limits and lengths | m/s, m |
| `DepartureTime` | scalar double | Departure time of the operation record | s |
| `GuidancetRef` | row vector | Reference time trajectory | s |
| `GuidanceVRef` | row vector | Reference speed trajectory | m/s |
| `GuidanceXRef` | row vector | Reference position trajectory | m |
| `GuidanceuRef` | row vector | Reference traction/braking control trajectory | dimensionless or normalized |
| `Addmissiblet` | `1 × 2` double | Admissible regulation time window | s |
| `Addmissiblex` | `1 × 2` double | Admissible regulation position window | m |

The `TrainPara` vector uses the following order:

| Index | Parameter | Unit |
|---|---|---|
| 1 | Maximum traction force per unit mass, `Fm` | N/kg |
| 2 | Maximum traction power per unit mass, `Pm` | W/kg |
| 3 | Rotating-mass coefficient, `gamma` | - |
| 4 | Davis resistance coefficient, `a0` | N/kg |
| 5 | Davis resistance coefficient, `a1` | N/(kg·m/s) |
| 6 | Davis resistance coefficient, `a2` | N/(kg·(m/s)^2) |
| 7 | Maximum braking force per unit mass, `Bm` | N/kg |
| 8 | Train mass, `m` | kg |
| 9 | Traction efficiency, `etaT` | - |
| 10 | Braking/regenerative efficiency, `etaB` | - |

The `RoadPara` matrix uses the following columns:

| Column | Meaning | Unit |
|---|---|---|
| 1 | Speed limit | m/s |
| 2 | Segment length | m |

The field names `Addmissiblet` and `Addmissiblex` are retained for consistency with the existing data file. They correspond to the admissible time and position windows used in the ERES regulation evaluation.

## 10. Function reference

### 10.1 `DEP_evaluation.m`

Syntax:

```matlab
[Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet)
```

Purpose:

Evaluates the deployable ERES power and delivered regulation energy of selected inter-stop operation records under a specified regulation case.

Inputs:

| Input | Description |
|---|---|
| `TrainConfiguration` | Structure array containing inter-stop operation data |
| `RegSet` | Cell array defining participating operation records, time step, regulation duration, regulation direction, and regulation start time |

Outputs:

| Output | Description |
|---|---|
| `Power` | Deployable ERES power over the specified duration in MW |
| `Energy` | Delivered regulation energy over the specified duration in MWh |
| `ChangeofPower` | Power-adjustment profile of each participating inter-stop operation record in MW |

Notes:

- The function evaluates one regulation direction at a time.
- The regulation duration should be provided as `[0 duration_min]`.
- The public example assumes a 60-second time step.
- The numerical outputs are reported as positive magnitudes for the evaluated direction.

### 10.2 `Aggregation_model.m`

Syntax:

```matlab
[EPC, ESC, RDR] = Aggregation_model(ChangeofPower_MultiplePeriod, RegDeployingPeriod_MultiplePeriod)
```

Purpose:

Builds an aggregated equivalent energy storage from deployable ERES power results over multiple regulation durations.

Inputs:

| Input | Description |
|---|---|
| `ChangeofPower_MultiplePeriod` | Cell array containing power-adjustment results for multiple regulation durations |
| `RegDeployingPeriod_MultiplePeriod` | Vector of tested regulation durations in minutes |

Outputs:

| Output | Description |
|---|---|
| `EPC` | Aggregated ERES power capacity in MW |
| `ESC` | Fitted storage-equivalent energy capacity in MWh |
| `RDR` | Regulation deployable region |

Notes:

- `Aggregation_model.m` should be run separately for discharge and charge regulation results.
- In the public example, the bidirectional ERES storage capacity is calculated as `ESC_dis + ESC_cha`.
- Regulation durations are supplied in minutes, and the resulting fitted energy capacity is reported in MWh.

### 10.3 `PlotResult.m`

Syntax:

```matlab
PlotResult(RDR_dis, Power_MultiplePeriod_dis, RDR_cha, Power_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod)
```

Purpose:

Plots the bidirectional regulation deployable region and the deployable power results across tested regulation durations.

Inputs:

| Input | Description |
|---|---|
| `RDR_dis` | Discharge regulation deployable region returned by `Aggregation_model.m` |
| `Power_MultiplePeriod_dis` | Discrete deployable discharge power values returned by `DEP_evaluation.m` |
| `RDR_cha` | Charge regulation deployable region returned by `Aggregation_model.m` |
| `Power_MultiplePeriod_cha` | Discrete deployable charge power values returned by `DEP_evaluation.m` |
| `RegDeployingPeriod_MultiplePeriod` | Vector of tested regulation durations in minutes |

Notes:

- Charge power is plotted as positive.
- Discharge power is plotted as negative.
- The sign convention is used only for visualization. The numerical outputs of `DEP_evaluation.m` and `Aggregation_model.m` are reported as positive magnitudes for each evaluated direction.

### 10.4 `check_environment.m`

Syntax:

```matlab
check_environment
```

Purpose:

Checks whether the repository files, YALMIP functions, and Gurobi solver are available in the current MATLAB environment.

## 11. Reproducing modified cases

To reproduce a different case, users should modify the following settings in `Example.m`:

1. operation-record subset: `RegSet{1}`;
2. regulation duration: `RegSet{3}`;
3. regulation direction: `RegSet{4}`;
4. regulation start time: `RegSet{5}`;

The time discretization `RegSet{2}` should normally remain `60` seconds for the public example unless the code is modified consistently.

For example, to evaluate both discharge and charge regulation at 10:05 using the first 30 inter-stop operation records:

```matlab
load('TrainConfiguration_example.mat');
TrainConfiguration = TrainConfiguration_example;

RegSet{1} = 1:30;
RegSet{2} = 60;
RegSet{5} = 36300;

RegDeployingPeriod_MultiplePeriod = 0:15;

% Discharge regulation
RegSet{4} = 1;

Power_MultiplePeriod_dis = zeros(size(RegDeployingPeriod_MultiplePeriod));
Energy_MultiplePeriod_dis = zeros(size(RegDeployingPeriod_MultiplePeriod));
ChangeofPower_MultiplePeriod_dis = cell(size(RegDeployingPeriod_MultiplePeriod));

for k = 1:length(RegDeployingPeriod_MultiplePeriod)
    RegDeployingPeriod = RegDeployingPeriod_MultiplePeriod(k);
    RegSet{3} = [0 RegDeployingPeriod];

    [Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);

    Power_MultiplePeriod_dis(k) = Power;
    Energy_MultiplePeriod_dis(k) = Energy;
    ChangeofPower_MultiplePeriod_dis{k} = ChangeofPower;
end

[EPC_dis, ESC_dis, RDR_dis] = Aggregation_model(ChangeofPower_MultiplePeriod_dis, RegDeployingPeriod_MultiplePeriod);

% Charge regulation
RegSet{4} = 2;

Power_MultiplePeriod_cha = zeros(size(RegDeployingPeriod_MultiplePeriod));
Energy_MultiplePeriod_cha = zeros(size(RegDeployingPeriod_MultiplePeriod));
ChangeofPower_MultiplePeriod_cha = cell(size(RegDeployingPeriod_MultiplePeriod));

for k = 1:length(RegDeployingPeriod_MultiplePeriod)
    RegDeployingPeriod = RegDeployingPeriod_MultiplePeriod(k);
    RegSet{3} = [0 RegDeployingPeriod];

    [Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);

    Power_MultiplePeriod_cha(k) = Power;
    Energy_MultiplePeriod_cha(k) = Energy;
    ChangeofPower_MultiplePeriod_cha{k} = ChangeofPower;
end

[EPC_cha, ESC_cha, RDR_cha] = Aggregation_model(ChangeofPower_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod);

fprintf('Aggregated ERES discharge power capacity: %.6f MW\n', EPC_dis);
fprintf('Aggregated ERES charge power capacity: %.6f MW\n', EPC_cha);
fprintf('Aggregated ERES storage capacity: %.6f MWh\n', ESC_dis + ESC_cha);

PlotResult(RDR_dis, Power_MultiplePeriod_dis, RDR_cha, Power_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod);
```

## 12. Replacing the example dataset

Users can replace `TrainConfiguration_example.mat` with another dataset if the new dataset follows the same structure described in Section 9.

The replacement dataset should contain a structure array with one element per inter-stop operation record. Each element must include the same fields, field dimensions, and units as `TrainConfiguration_example`.

A typical replacement workflow is:

```matlab
load('MyTrainConfiguration.mat');
TrainConfiguration = MyTrainConfiguration;

RegSet{1} = 1:numel(TrainConfiguration);
RegSet{2} = 60;
RegSet{3} = [0 5];
RegSet{4} = 1;
RegSet{5} = 36000;

[Power, Energy, ChangeofPower] = DEP_evaluation(TrainConfiguration, RegSet);
```

Before using a new dataset, check that:

- all required fields are present;
- all time variables are in seconds;
- speed is in m/s;
- position and segment length are in m;
- mass is in kg;
- the admissible regulation window is consistent with the reference trajectory;
- the selected regulation start time overlaps with the operation records to be evaluated.

## 13. Troubleshooting

### 13.1 `Undefined function or variable 'sdpvar'`

This indicates that YALMIP is not installed or not on the MATLAB path.

Check the YALMIP path:

```matlab
which sdpvar
```

If MATLAB cannot find `sdpvar`, add YALMIP to the path:

```matlab
addpath(genpath('path/to/yalmip'))
```

### 13.2 `Solver not found: gurobi`

This indicates that Gurobi is not available to YALMIP.

Check whether MATLAB can find Gurobi:

```matlab
which gurobi
```

Also check that the Gurobi license is valid.

### 13.3 Gurobi license error

If Gurobi is installed but the license is not found, follow the Gurobi license installation instructions for your operating system and verify that the license file is accessible.

After configuring the license, restart MATLAB and rerun:

```matlab
check_environment
```

### 13.4 `Undefined function or variable 'DEP_evaluation'`

This indicates that the repository folder is not on the MATLAB path.

From the repository root folder, run:

```matlab
addpath(genpath(pwd))
```

### 13.5 Missing data file

If MATLAB reports that `TrainConfiguration_example.mat` cannot be found, make sure that the file is located in the repository root folder or that the folder containing the file is on the MATLAB path.

### 13.6 Dimension or field-name errors in `TrainConfiguration`

The input data must follow the structure described in Section 9. In particular, each inter-stop operation record must include the fields:

```matlab
TrainPara
RoadPara
DepartureTime
GuidancetRef
GuidanceVRef
GuidanceXRef
GuidanceuRef
Addmissiblet
Addmissiblex
```

If a user replaces `TrainConfiguration_example.mat` with another dataset, the new dataset must use the same field names, dimensions, and units.
