# Electrified Rail-based Energy Storage

This repository provides the MATLAB implementation used to convert
railway-operation inputs into the power and energy capacities of electrified
rail-based energy storage (ERES).

The code accompanies the research article:

**Transforming electrified railway into mechanical energy storage for energy
transition**

## Scope

The repository covers the railway-side calculation:

1. load a railway operation input;
2. evaluate deployable ERES power for regulation durations from 0 to 15
   minutes;
3. evaluate the discharge and charge directions separately;
4. aggregate the multi-duration results into direction-specific power and
   energy capacities; and
5. calculate the total ERES energy storage capacity.

The companion data package contains 2,688 self-contained input cases. The
complete SWITCH model configuration and power-system input bundle
are provided separately in the `ERES_SWITCH` directory of this repository.

## Direction definitions

The public workflow uses the same terminology as the manuscript:

- **Charge:** additional electrical energy absorption relative to the
  scheduled railway-operation baseline.
- **Discharge:** a reduction in net electrical energy absorption relative to
  the scheduled baseline, including reduced traction demand or regenerative
  output.

Charge and discharge capacities are returned as positive magnitudes. In the
bidirectional plot, charge power is shown as positive and discharge power as
negative.

## Software requirements

The tested environment is:

| Component | Tested version |
|---|---|
| MATLAB | R2023b |
| YALMIP | 20230622 |
| Gurobi Optimizer | 11.0.2 |
| Operating system | Windows 10 |

Required software:

- MATLAB;
- YALMIP on the MATLAB path;
- Gurobi Optimizer and its MATLAB interface; and
- a valid Gurobi license.

Run the environment check before evaluating an input:

```matlab
check_environment
```

The final line should be:

```text
Environment check passed.
```

## Repository files

| File | Description |
|---|---|
| `TrainConfiguration_example.mat` | Bundled example input |
| `Example.m` | Evaluates and plots the bundled example |
| `run_ERES_case.m` | Main capacity-evaluation entry point |
| `load_ERES_case.m` | Loads an input structure or MAT file |
| `DEP_evaluation.m` | Evaluates deployable power for one direction and duration |
| `Aggregation_model.m` | Builds the storage-equivalent capacity model |
| `PlotResult.m` | Plots the bidirectional deployable region |
| `check_environment.m` | Checks MATLAB, YALMIP, and Gurobi |

`run_ERES_case.m` is the canonical calculation used by both the bundled
example and the companion input cases.

## Bundled example

From the repository folder, run:

```matlab
Result = Example();
```

`Example.m` loads only `TrainConfiguration_example.mat`. It evaluates both
directions, reports the manuscript-facing capacities, and generates the
bidirectional deployable-power plot.

The expected capacities of the bundled example are approximately:

```text
ERES discharge power capacity: 511.699192133 MW
ERES charge power capacity: 388.191921760 MW
ERES energy storage capacity: 20.5997042119 MWh
```

Small solver-dependent differences at numerical-tolerance scale may occur.
The bundled input retains the full reference-trajectory resolution, so
the complete example can require tens of minutes depending on the computer
and optimization environment.

## Companion data

The data are distributed across 12 ZIP archives, with 224 cases in each
archive. Download and extract all 12 archives into the same destination to
obtain the following layout:

```text
cases/
|-- Case_0001.mat
|-- ...
`-- Case_2688.mat
```

Each materialized case MAT file contains:

- `TrainConfiguration`: a nonempty `1-by-N` structure containing every
  operation record required for the calculation; and
- `CaseMetadata`: case and dataset metadata.

Evaluate one companion input directly:

```matlab
dataRoot = "path/to/extracted/data";
caseFile = fullfile(dataRoot, "cases", "Case_0001.mat");
Result = run_ERES_case(caseFile);
```

The same function also accepts an already loaded structure:

```matlab
inputData = load(caseFile, "TrainConfiguration");
Result = run_ERES_case(inputData.TrainConfiguration);
```

Cases are independent and can be assigned to separate MATLAB processes or
computers. Runtime depends strongly on the number and optimization complexity
of the operation records in each input.

## Returned capacities

The manuscript-facing results are:

```matlab
Result.Discharge.PowerCapacity
Result.Charge.PowerCapacity
Result.Discharge.EnergyCapacity
Result.Charge.EnergyCapacity
Result.EnergyStorageCapacity
```

Power capacity is reported in MW and energy capacity in MWh. The total energy
storage capacity is calculated as:

```matlab
Result.EnergyStorageCapacity = ...
    Result.Discharge.EnergyCapacity + Result.Charge.EnergyCapacity;
```

`Result.CaseMetadata` contains the optional metadata loaded from a case MAT
file. It is an empty structure when the input contains only
`TrainConfiguration` or when a structure is passed directly.

Each direction also contains:

- `PowerByDuration`;
- `EnergyByDuration`;
- `ParticipatingRecordCountByDuration`; and
- `DeployableRegion`.

## Time convention

The bundled example and the materialized companion cases use
**regulation-relative time**. Time zero is the start of the evaluated
regulation request, so:

```matlab
RegSet{5} = 0;
```

This value is set by `run_ERES_case.m`. Departure and trajectory times may be
negative when a railway operation starts before the regulation request.
Applying an absolute timetable value to a materialized case shifts
its operation records away from the regulation window and can produce zero
capacities.

## Input structure

Each element of `TrainConfiguration` represents one railway-operation record
and contains:

| Field | Meaning |
|---|---|
| `TrainPara` | Train mass, force, power, resistance, and efficiency parameters |
| `RoadPara` | Track-section speed limits and lengths |
| `DepartureTime` | Departure time relative to the regulation start; may be negative |
| `GuidancetRef` | Reference trajectory time relative to the regulation start |
| `GuidanceVRef` | Reference velocity |
| `GuidanceXRef` | Reference position |
| `GuidanceuRef` | Reference control |
| `Addmissiblet` | Admissible interval relative to the regulation start |
| `Addmissiblex` | Admissible regulation-position interval |

The four reference-trajectory vectors are aligned and have equal lengths.

`TrainPara` uses the following order:

| Index | Parameter | Unit |
|---:|---|---|
| 1 | Maximum traction force per unit mass | N/kg |
| 2 | Maximum traction power per unit mass | W/kg |
| 3 | Rotating-mass coefficient | - |
| 4 | Davis resistance coefficient `a0` | N/kg |
| 5 | Davis resistance coefficient `a1` | N/(kg m/s) |
| 6 | Davis resistance coefficient `a2` | N/(kg (m/s)^2) |
| 7 | Maximum braking force per unit mass | N/kg |
| 8 | Train mass | kg |
| 9 | Traction efficiency | - |
| 10 | Braking/regenerative efficiency | - |

`RoadPara` contains speed limit in column 1 (m/s) and section length in
column 2 (m). Additional columns are permitted and are not used by the
current capacity calculation.

## Lower-level calculation

`run_ERES_case.m` should normally be used for reproduction. For an individual
direction and duration:

```matlab
caseFile = "path/to/extracted/data/cases/Case_0001.mat";
[TrainConfiguration, CaseMetadata] = load_ERES_case(caseFile);

RegSet = cell(1, 6);
RegSet{1} = 1:numel(TrainConfiguration);
RegSet{2} = 60;
RegSet{3} = [0 5];
RegSet{4} = 1;
RegSet{5} = 0;
RegSet{6} = 15;

[Power, Energy, ChangeOfPower] = ...
    DEP_evaluation(TrainConfiguration, RegSet);
```

The direction values are:

- `RegSet{4} = 1`: discharge;
- `RegSet{4} = 2`: charge.

`RegSet{6}` is the model horizon in minutes. It is optional when calling
`DEP_evaluation.m` directly and defaults to 15 minutes. The public
`run_ERES_case.m` workflow sets it explicitly to 15 minutes.

`DEP_evaluation.m` validates the required input fields, trajectory-vector
dimensions, regulation settings, solver status, and numerical solver outputs.
Invalid inputs and unsuccessful solves raise errors with identifiers beginning
with `DEP_evaluation:`.

For the zero-duration power calculation, `run_ERES_case.m` uses a 20-second
discretization. For durations from 1 to 15 minutes, it uses a 60-second
discretization.

`Aggregation_model.m` converts the power-adjustment results across durations
into the corresponding direction-specific power capacity, energy capacity,
and deployable region. `run_ERES_case.m` constructs the required
multi-duration `ChangeOfPower` cell array and calls `Aggregation_model.m`
separately for discharge and charge. Users reproducing
the manuscript-facing capacities should call `run_ERES_case.m` rather than
calling the aggregation function with an incomplete single-duration result.

## Troubleshooting

### All capacities are zero

Confirm that the input uses regulation-relative time and that:

```matlab
RegSet{5} = 0;
```

### PlotResult reports an invalid axis range

`PlotResult.m` includes a fallback range for all-zero diagnostic results. If
all calculated values are zero, check the time convention and input fields.

### Gurobi is unavailable

Run:

```matlab
check_environment
```

Confirm that YALMIP is on the MATLAB path, the Gurobi MATLAB interface is
installed, and the license is valid.

## License

See `LICENSE`.
