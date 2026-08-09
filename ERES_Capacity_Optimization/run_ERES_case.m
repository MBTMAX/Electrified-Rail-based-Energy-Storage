function Result = run_ERES_case(caseInput)
%RUN_ERES_CASE Evaluate charge and discharge capacities of one ERES case.
%   Result = RUN_ERES_CASE(TrainConfiguration) accepts a 1-by-N structure.
%   Result = RUN_ERES_CASE(caseFile) loads TrainConfiguration from a MAT file.

[TrainConfiguration, CaseMetadata] = load_ERES_case(caseInput);
durations = 0:15;

Result = struct;
Result.CaseMetadata = CaseMetadata;
Result.Discharge = evaluateDirection(TrainConfiguration, 1, durations);
Result.Charge = evaluateDirection(TrainConfiguration, 2, durations);
Result.EnergyStorageCapacity = Result.Discharge.EnergyCapacity + ...
    Result.Charge.EnergyCapacity;
end

function DirectionResult = evaluateDirection(TrainConfiguration, direction, durations)
powerByDuration = zeros(size(durations));
energyByDuration = zeros(size(durations));
changeOfPower = cell(size(durations));
participatingRecordCount = zeros(size(durations));

RegSet = cell(1, 6);
RegSet{1} = 1:numel(TrainConfiguration);
RegSet{4} = direction;
RegSet{5} = 0;
RegSet{6} = 15;

for k = 1:numel(durations)
    duration = durations(k);
    if duration == 0
        RegSet{2} = 20;
    else
        RegSet{2} = 60;
    end
    RegSet{3} = [0 duration];
    [powerByDuration(k), energyByDuration(k), changeOfPower{k}] = ...
        DEP_evaluation(TrainConfiguration, RegSet);
    participatingRecordCount(k) = nnz( ...
        any(abs(changeOfPower{k}) > 1e-10, 2));
end

[powerCapacity, energyCapacity, deployableRegion] = ...
    Aggregation_model(changeOfPower, durations);

DirectionResult = struct;
DirectionResult.PowerCapacity = powerCapacity;
DirectionResult.EnergyCapacity = energyCapacity;
DirectionResult.PowerByDuration = powerByDuration;
DirectionResult.EnergyByDuration = energyByDuration;
DirectionResult.ParticipatingRecordCountByDuration = ...
    participatingRecordCount;
DirectionResult.DeployableRegion = deployableRegion;
end
