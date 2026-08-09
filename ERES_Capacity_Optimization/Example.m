function Result = Example()
%EXAMPLE Evaluate and plot the bundled ERES example.

repositoryRoot = fileparts(mfilename('fullpath'));
exampleFile = fullfile(repositoryRoot, 'TrainConfiguration_example.mat');
assert(isfile(exampleFile), ...
    'The bundled example input was not found: %s', exampleFile);

check_environment();
fprintf('Evaluating the bundled example input...\n');
timer = tic;
Result = run_ERES_case(exampleFile);
elapsedSeconds = toc(timer);

fprintf('ERES discharge power capacity: %.12g MW\n', ...
    Result.Discharge.PowerCapacity);
fprintf('ERES charge power capacity: %.12g MW\n', ...
    Result.Charge.PowerCapacity);
fprintf('ERES energy storage capacity: %.12g MWh\n', ...
    Result.EnergyStorageCapacity);
fprintf('Elapsed time: %.1f s\n', elapsedSeconds);

durations = 0:15;
PlotResult( ...
    Result.Discharge.DeployableRegion, ...
    Result.Discharge.PowerByDuration, ...
    Result.Charge.DeployableRegion, ...
    Result.Charge.PowerByDuration, ...
    durations);
end
