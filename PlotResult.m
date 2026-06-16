function PlotResult(RDR_dis, Power_MultiplePeriod_dis, RDR_cha, Power_MultiplePeriod_cha, RegDeployingPeriod_MultiplePeriod)
%PLOTRESULT Plot bidirectional deployable ERES evaluation and aggregation model
%
% Sign convention:
%   Charge power is plotted as positive.
%   Discharge power is plotted as negative.
%
% Inputs:
%   RDR_dis:
%       Regulation deployable region for discharge regulation.
%       Row 1: regulation duration, min.
%       Row 2: deployable power, MW.
%
%   Power_MultiplePeriod_dis:
%       Discrete deployable discharge power values from DEP_evaluation.m, MW.
%
%   RDR_cha:
%       Regulation deployable region for charge regulation.
%       Row 1: regulation duration, min.
%       Row 2: deployable power, MW.
%
%   Power_MultiplePeriod_cha:
%       Discrete deployable charge power values from DEP_evaluation.m, MW.
%
%   RegDeployingPeriod_MultiplePeriod:
%       Tested regulation durations, min.

figure;
hold on;

set(gcf, 'Position', [100, 100, 650, 520]);
set(gca, 'position', [0.18 0.18 0.74 0.72]);

% Convert to row vectors for robust plotting
RegDeployingPeriod_MultiplePeriod = RegDeployingPeriod_MultiplePeriod(:)';
Power_MultiplePeriod_dis = Power_MultiplePeriod_dis(:)';
Power_MultiplePeriod_cha = Power_MultiplePeriod_cha(:)';

% Sign convention
RDR_dis_plot = RDR_dis;
RDR_cha_plot = RDR_cha;

RDR_dis_plot(2,:) = -abs(RDR_dis_plot(2,:));
RDR_cha_plot(2,:) =  abs(RDR_cha_plot(2,:));

Power_dis_plot = -abs(Power_MultiplePeriod_dis);
Power_cha_plot =  abs(Power_MultiplePeriod_cha);

% Plot aggregation-model curves
agg_dis = plot(RDR_dis_plot(1,:), RDR_dis_plot(2,:), '-', 'LineWidth', 1.2);
agg_cha = plot(RDR_cha_plot(1,:), RDR_cha_plot(2,:), '-', 'LineWidth', 1.2);

% Plot discrete deployable evaluation points
dep_dis = scatter(RegDeployingPeriod_MultiplePeriod, Power_dis_plot, 36, 'filled');
dep_cha = scatter(RegDeployingPeriod_MultiplePeriod, Power_cha_plot, 36, 'filled');

% Axis settings
Xlim = RegDeployingPeriod_MultiplePeriod(end);
xlim([0 Xlim]);
xticks(linspace(0, Xlim, 4));

Ylim = 1.2 * max([
    abs(Power_dis_plot), ...
    abs(Power_cha_plot), ...
    abs(RDR_dis_plot(2,:)), ...
    abs(RDR_cha_plot(2,:))
]);

ylim([-Ylim Ylim]);

% Zero reference line
plot([0 Xlim], [0 0], 'k-', 'LineWidth', 0.8, 'HandleVisibility', 'off');

xlabel('Regulation duration (min)');
ylabel('Deployable ERES power (MW)');

legend([dep_cha, agg_cha, dep_dis, agg_dis], ...
    'Charge deployable ERES evaluation', ...
    'Charge aggregation model', ...
    'Discharge deployable ERES evaluation', ...
    'Discharge aggregation model', ...
    'Location', 'best');

box on;
hold off;

end