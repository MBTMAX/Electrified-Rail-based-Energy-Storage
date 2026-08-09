function PlotResult(dischargeDeployableRegion, dischargePowerByDuration, ...
    chargeDeployableRegion, chargePowerByDuration, durations)
%PLOTRESULT Plot bidirectional ERES evaluation and aggregation results.
%
% Sign convention:
%   Charge power is plotted as positive.
%   Discharge power is plotted as negative.
%
% Inputs:
%   dischargeDeployableRegion:
%       Regulation deployable region for discharge regulation.
%       Row 1: regulation duration, min.
%       Row 2: deployable power, MW.
%
%   dischargePowerByDuration:
%       Discrete deployable discharge power values from DEP_evaluation.m, MW.
%
%   chargeDeployableRegion:
%       Regulation deployable region for charge regulation.
%       Row 1: regulation duration, min.
%       Row 2: deployable power, MW.
%
%   chargePowerByDuration:
%       Discrete deployable charge power values from DEP_evaluation.m, MW.
%
%   durations:
%       Tested regulation durations, min.

figure;
hold on;

set(gcf, 'Position', [100, 100, 650, 520]);
set(gca, 'position', [0.18 0.18 0.74 0.72]);

% Convert to row vectors for robust plotting.
durations = durations(:)';
dischargePowerByDuration = dischargePowerByDuration(:)';
chargePowerByDuration = chargePowerByDuration(:)';

dischargeRegionToPlot = dischargeDeployableRegion;
chargeRegionToPlot = chargeDeployableRegion;

dischargeRegionToPlot(2, :) = -abs(dischargeRegionToPlot(2, :));
chargeRegionToPlot(2, :) = abs(chargeRegionToPlot(2, :));

dischargePowerToPlot = -abs(dischargePowerByDuration);
chargePowerToPlot = abs(chargePowerByDuration);
evaluationPoint = durations > 0;

dischargeAggregationPlot = plot( ...
    dischargeRegionToPlot(1, :), dischargeRegionToPlot(2, :), ...
    '-', 'LineWidth', 1.2);
chargeAggregationPlot = plot( ...
    chargeRegionToPlot(1, :), chargeRegionToPlot(2, :), ...
    '-', 'LineWidth', 1.2);

dischargeEvaluationPlot = scatter( ...
    durations(evaluationPoint), dischargePowerToPlot(evaluationPoint), ...
    36, 'filled');
chargeEvaluationPlot = scatter( ...
    durations(evaluationPoint), chargePowerToPlot(evaluationPoint), ...
    36, 'filled');

maximumDuration = durations(end);
xlim([0 maximumDuration]);
xticks(linspace(0, maximumDuration, 4));

maximumPower = 1.2 * max([
    abs(dischargePowerToPlot(evaluationPoint)), ...
    abs(chargePowerToPlot(evaluationPoint)), ...
    abs(dischargeRegionToPlot(2, :)), ...
    abs(chargeRegionToPlot(2, :))
]);

if ~isfinite(maximumPower) || maximumPower <= 0
    maximumPower = 1;
end
ylim([-maximumPower maximumPower]);

% Zero reference line
plot([0 maximumDuration], [0 0], 'k-', ...
    'LineWidth', 0.8, 'HandleVisibility', 'off');

xlabel('Regulation duration (min)');
ylabel('Deployable ERES power (MW)');

legend([chargeEvaluationPlot, chargeAggregationPlot, ...
    dischargeEvaluationPlot, dischargeAggregationPlot], ...
    'Charge deployable ERES evaluation', ...
    'Charge aggregation model', ...
    'Discharge deployable ERES evaluation', ...
    'Discharge aggregation model', ...
    'Location', 'best');

box on;
hold off;
end
